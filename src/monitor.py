import duckdb
import pandas as pd
import pandas as pd
import numpy as np
import joblib
import torch
import torch.nn as nn

# --- Load saved artifacts (from Phase 2 — no retraining here) ---
scaler = joblib.load("data/bilstm_scaler.joblib")
SIGNAL_METRICS = joblib.load("data/signal_metrics.joblib")
WINDOW = joblib.load("data/window_size.joblib")


class BiLSTMClassifier(nn.Module):
    def __init__(self, n_features, hidden=32):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(hidden * 2, 16), nn.ReLU(), nn.Dropout(0.3), nn.Linear(16, 1))

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze(-1)


_model = BiLSTMClassifier(n_features=len(SIGNAL_METRICS))
_model.load_state_dict(torch.load("data/bilstm_model.pt", map_location="cpu"))
_model.eval()


def score_latest(equipment_id: str) -> dict:
    """Hybrid detector: rule OR BiLSTM. Fast — reads only one device's recent
    rows from DuckDB, no full-dataset pivot or retraining."""
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    rows = con.sql(f"""
        SELECT timestamp, metric, value FROM sensor_readings
        WHERE equipment_id = '{equipment_id}'
        ORDER BY timestamp
    """).df()
    con.close()

    if rows.empty:
        return {"equipment_id": equipment_id, "is_anomaly": False, "severity": 0.0, "error": "no data"}

    wide = rows.pivot_table(index="timestamp", columns="metric", values="value").reset_index()
    wide = wide.sort_values("timestamp")
    vals = wide[SIGNAL_METRICS].values.astype(np.float32)

    window = vals[-WINDOW:]
    if len(window) < WINDOW:
        pad = np.zeros((WINDOW - len(window), len(SIGNAL_METRICS)), dtype=np.float32)
        window = np.vstack([pad, window])

    window_scaled = scaler.transform(window).reshape(1, WINDOW, len(SIGNAL_METRICS))
    with torch.no_grad():
        proba = torch.sigmoid(_model(torch.tensor(window_scaled, dtype=torch.float32))).item()

    metric4_val = window[-1, SIGNAL_METRICS.index("metric4")]
    rule_fired = bool(metric4_val > 0)
    model_fired = proba >= 0.5
    is_anomaly = rule_fired or model_fired

    triggered_by = "none"
    if rule_fired and model_fired:
        triggered_by = "both"
    elif rule_fired:
        triggered_by = "rule"
    elif model_fired:
        triggered_by = "model"

    return {
        "equipment_id": equipment_id,
        "timestamp": str(wide["timestamp"].iloc[-1]),
        "is_anomaly": is_anomaly,
        "severity": float(max(proba, 1.0 if rule_fired else 0.0)),
        "triggered_by": triggered_by,
        "metric4_value": float(metric4_val),
    }


if __name__ == "__main__":
    # quick sanity test with a real device from the dataset
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    sample_device = con.sql("SELECT DISTINCT equipment_id FROM sensor_readings LIMIT 1").df().iloc[0, 0]
    con.close()
    print(score_latest(sample_device))


def score_as_of(equipment_id: str, as_of_date) -> dict:
    """Same hybrid detector as score_latest(), but scored using only data
    up to a given simulated date — this is what powers the Live Triage
    Console's 'Next Timeframe' simulation."""
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    rows = con.sql(f"""
        SELECT timestamp, metric, value FROM sensor_readings
        WHERE equipment_id = '{equipment_id}' AND timestamp <= '{as_of_date}'
        ORDER BY timestamp
    """).df()
    con.close()

    if rows.empty:
        return {"equipment_id": equipment_id, "is_anomaly": False, "severity": 0.0, "as_of": str(as_of_date), "no_data_yet": True}

    wide = rows.pivot_table(index="timestamp", columns="metric", values="value").reset_index()
    wide = wide.sort_values("timestamp")
    vals = wide[SIGNAL_METRICS].values.astype(np.float32)

    window = vals[-WINDOW:]
    if len(window) < WINDOW:
        pad = np.zeros((WINDOW - len(window), len(SIGNAL_METRICS)), dtype=np.float32)
        window = np.vstack([pad, window])

    window_scaled = scaler.transform(window).reshape(1, WINDOW, len(SIGNAL_METRICS))
    with torch.no_grad():
        proba = torch.sigmoid(_model(torch.tensor(window_scaled, dtype=torch.float32))).item()

    metric4_val = window[-1, SIGNAL_METRICS.index("metric4")]
    rule_fired = bool(metric4_val > 0)
    model_fired = proba >= 0.5
    is_anomaly = rule_fired or model_fired

    triggered_by = "none"
    if rule_fired and model_fired:
        triggered_by = "both"
    elif rule_fired:
        triggered_by = "rule"
    elif model_fired:
        triggered_by = "model"

    return {
        "equipment_id": equipment_id,
        "as_of": str(as_of_date),
        "timestamp": str(wide["timestamp"].iloc[-1]),
        "is_anomaly": is_anomaly,
        "severity": float(max(proba, 1.0 if rule_fired else 0.0)),
        "triggered_by": triggered_by,
        "metric4_value": float(metric4_val),
    }


def get_issue_onset(equipment_id: str, as_of_date) -> dict:
    """Find the actual date the anomaly condition began, not just the date
    we happened to scan and notice it. For rule-triggered flags, walks
    backward from as_of_date to find the start of the current metric4>0
    streak. For model-only flags (no clean single-metric trigger), returns
    None for onset_date since the BiLSTM's signal is a 14-day pattern, not
    a single dated event."""
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    rows = con.sql(f"""
        SELECT timestamp, value FROM sensor_readings
        WHERE equipment_id = '{equipment_id}' AND metric = 'metric4' AND timestamp <= '{as_of_date}'
        ORDER BY timestamp DESC
    """).df()
    con.close()

    if rows.empty or rows.iloc[0]["value"] <= 0:
        return {"onset_date": None}

    onset = rows.iloc[0]["timestamp"]
    for _, row in rows.iterrows():
        if row["value"] > 0:
            onset = row["timestamp"]
        else:
            break

    return {"onset_date": str(pd.Timestamp(onset).date())}


def get_issue_onset(equipment_id: str, as_of_date) -> dict:
    """Find the actual date the anomaly condition began, not just the date
    we happened to scan and notice it. For rule-triggered flags, walks
    backward from as_of_date to find the start of the current metric4>0
    streak. For model-only flags (no clean single-metric trigger), returns
    None for onset_date since the BiLSTM's signal is a 14-day pattern, not
    a single dated event."""
    con = duckdb.connect("data/fabcast.duckdb", read_only=True)
    rows = con.sql(f"""
        SELECT timestamp, value FROM sensor_readings
        WHERE equipment_id = '{equipment_id}' AND metric = 'metric4' AND timestamp <= '{as_of_date}'
        ORDER BY timestamp DESC
    """).df()
    con.close()

    if rows.empty or rows.iloc[0]["value"] <= 0:
        return {"onset_date": None}

    onset = rows.iloc[0]["timestamp"]
    for _, row in rows.iterrows():
        if row["value"] > 0:
            onset = row["timestamp"]
        else:
            break

    return {"onset_date": str(pd.Timestamp(onset).date())}
