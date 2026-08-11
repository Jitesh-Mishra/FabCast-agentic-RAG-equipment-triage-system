import duckdb
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, average_precision_score

torch.manual_seed(42)

# =======================================================================
# 1. Load raw readings from DuckDB, rebuild per-device time-ordered series
# =======================================================================
con = duckdb.connect("data/fabcast.duckdb")
long_df = con.sql("SELECT * FROM sensor_readings").df()
labels = con.sql("SELECT * FROM failure_labels").df()
con.close()

wide = long_df.pivot_table(
    index=["equipment_id", "timestamp"], columns="metric", values="value"
).reset_index()
wide = wide.merge(labels, on=["equipment_id", "timestamp"], how="left")
wide = wide.sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)

# Confirmed via hand diagnostics: these 4 metrics carry real signal;
# metric1/3/5/6/8 were dropped as noise, near-constant, or duplicate.
SIGNAL_METRICS = ["metric2", "metric4", "metric7", "metric9"]
WINDOW = 14

# =======================================================================
# 2. Build sliding 14-day windows per device (BiLSTM input)
# =======================================================================
sequences, targets, meta = [], [], []
for device, g in wide.groupby("equipment_id"):
    g = g.sort_values("timestamp").reset_index(drop=True)
    vals = g[SIGNAL_METRICS].values.astype(np.float32)
    fails = g["failure"].values
    dates = g["timestamp"].values
    for i in range(len(g)):
        start = max(0, i - WINDOW + 1)
        window = vals[start:i + 1]
        if len(window) < WINDOW:
            pad = np.zeros((WINDOW - len(window), len(SIGNAL_METRICS)), dtype=np.float32)
            window = np.vstack([pad, window])
        sequences.append(window)
        targets.append(fails[i])
        meta.append((device, dates[i]))

X = np.stack(sequences)              # (N, 14, 4)
y = np.array(targets)
meta_df = pd.DataFrame(meta, columns=["equipment_id", "timestamp"])
N, T, F = X.shape
print(f"Sequences: {X.shape}, positives: {y.sum():.0f}/{len(y)}")

# =======================================================================
# 3. Chronological train / val / test split (same discipline throughout)
# =======================================================================
order = meta_df.sort_values("timestamp").index.values
n = len(order)
train_end, val_end = int(n * 0.60), int(n * 0.80)
train_idx, val_idx, test_idx = order[:train_end], order[train_end:val_end], order[val_end:]

print(f"Train: {len(train_idx):,} ({y[train_idx].sum():.0f} failures)")
print(f"Val:   {len(val_idx):,} ({y[val_idx].sum():.0f} failures)")
print(f"Test:  {len(test_idx):,} ({y[test_idx].sum():.0f} failures)")

scaler = StandardScaler()
scaler.fit(X[train_idx].reshape(-1, F))
X_scaled = scaler.transform(X.reshape(-1, F)).reshape(N, T, F)

# Undersample negatives in TRAIN ONLY for tractable training; val/test
# keep the true, realistic imbalance for an honest evaluation.
rng = np.random.default_rng(42)
train_pos = train_idx[y[train_idx] == 1]
train_neg = train_idx[y[train_idx] == 0]
train_neg_sample = rng.choice(train_neg, size=min(len(train_neg), len(train_pos) * 50), replace=False)
train_use = np.concatenate([train_pos, train_neg_sample])
rng.shuffle(train_use)

device_t = "cuda" if torch.cuda.is_available() else "cpu"
X_train_t = torch.tensor(X_scaled[train_use], dtype=torch.float32).to(device_t)
y_train_t = torch.tensor(y[train_use], dtype=torch.float32).to(device_t)
X_val_t = torch.tensor(X_scaled[val_idx], dtype=torch.float32).to(device_t)
y_val_t = torch.tensor(y[val_idx], dtype=torch.float32).to(device_t)
X_test_t = torch.tensor(X_scaled[test_idx], dtype=torch.float32).to(device_t)
y_test_np = y[test_idx]

# =======================================================================
# 4. BiLSTM model
# =======================================================================
class BiLSTMClassifier(nn.Module):
    def __init__(self, n_features, hidden=32):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(hidden * 2, 16), nn.ReLU(), nn.Dropout(0.3), nn.Linear(16, 1))

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze(-1)


model = BiLSTMClassifier(n_features=F).to(device_t)
criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([5.0]).to(device_t))
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

best_val_ap, best_state = -1, None
EPOCHS, BATCH = 30, 256
for epoch in range(EPOCHS):
    model.train()
    perm = torch.randperm(len(X_train_t))
    for i in range(0, len(perm), BATCH):
        idx = perm[i:i + BATCH]
        optimizer.zero_grad()
        loss = criterion(model(X_train_t[idx]), y_train_t[idx])
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        val_probs = torch.sigmoid(model(X_val_t)).cpu().numpy()
    val_ap = average_precision_score(y_val_t.cpu().numpy(), val_probs)
    if val_ap > best_val_ap:
        best_val_ap = val_ap
        best_state = {k: v.clone() for k, v in model.state_dict().items()}

model.load_state_dict(best_state)
print(f"Best validation AP: {best_val_ap:.4f}")

# =======================================================================
# 5. Evaluate once on TEST — model alone, rule alone, and the hybrid
# =======================================================================
model.eval()
with torch.no_grad():
    test_probs = torch.sigmoid(model(X_test_t)).cpu().numpy()

rule_signal_test = X[test_idx, -1, SIGNAL_METRICS.index("metric4")]
rule_pred = rule_signal_test > 0
model_pred = test_probs >= 0.5
hybrid_pred = rule_pred | model_pred

print("\n--- TEST recall by approach ---")
print(f"Rule alone:   {y_test_np[rule_pred].sum():.0f}/{y_test_np.sum():.0f}")
print(f"Model alone:  {y_test_np[model_pred].sum():.0f}/{y_test_np.sum():.0f}")
print(f"Hybrid (OR):  {y_test_np[hybrid_pred].sum():.0f}/{y_test_np.sum():.0f}  <- deployed detector")
print(f"\nBaseline (random) AP: {y_test_np.sum()/len(y_test_np):.4f}")
print(f"Model AP:             {average_precision_score(y_test_np, test_probs):.4f}")

print("\n--- Hybrid classification report ---")
print(classification_report(y_test_np, hybrid_pred.astype(int), target_names=["normal", "failure"], zero_division=0))

# =======================================================================
# 6. Save deployment artifacts
# =======================================================================
torch.save(model.state_dict(), "data/bilstm_model.pt")
joblib.dump(scaler, "data/bilstm_scaler.joblib")
joblib.dump(SIGNAL_METRICS, "data/signal_metrics.joblib")
joblib.dump(WINDOW, "data/window_size.joblib")
print("\nSaved: data/bilstm_model.pt, data/bilstm_scaler.joblib")


# =======================================================================
# 7. score_latest() — the function the Monitor Agent calls in Phase 4.
#    Hybrid logic: flag if EITHER the simple rule fires OR the BiLSTM's
#    probability crosses 0.5. Severity reported is whichever signal is
#    stronger, normalized to a comparable 0-1 scale.
# =======================================================================
def score_latest(equipment_id: str) -> dict:
    device_rows = wide[wide.equipment_id == equipment_id].sort_values("timestamp")
    if device_rows.empty:
        return {"equipment_id": equipment_id, "is_anomaly": False, "severity": 0.0, "error": "no data"}

    vals = device_rows[SIGNAL_METRICS].values.astype(np.float32)
    window = vals[-WINDOW:]
    if len(window) < WINDOW:
        pad = np.zeros((WINDOW - len(window), len(SIGNAL_METRICS)), dtype=np.float32)
        window = np.vstack([pad, window])

    window_scaled = scaler.transform(window).reshape(1, WINDOW, len(SIGNAL_METRICS))
    with torch.no_grad():
        proba = torch.sigmoid(model(torch.tensor(window_scaled, dtype=torch.float32).to(device_t))).item()

    metric4_val = window[-1, SIGNAL_METRICS.index("metric4")]
    rule_fired = metric4_val > 0

    is_anomaly = bool(rule_fired or proba >= 0.5)
    severity = max(proba, 1.0 if rule_fired else 0.0)

    return {
        "equipment_id": equipment_id,
        "timestamp": str(device_rows["timestamp"].iloc[-1]),
        "is_anomaly": is_anomaly,
        "severity": float(severity),
        "triggered_by": "rule" if rule_fired and proba < 0.5 else ("model" if proba >= 0.5 and not rule_fired else "both" if rule_fired else "none"),
    }
