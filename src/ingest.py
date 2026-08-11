import pandas as pd
import duckdb


df = pd.read_csv("data/raw/predictive_maintenance.csv")

# print(df.info())

df["date"] = pd.to_datetime(df["date"],format="%m/%d/%Y")
df = df.rename(columns={"date": "timestamp", "device":"equipment_id" })

metric_cols = [cols for cols in df.columns if cols.startswith("metric")]
long_df = df.melt(
    id_vars=["equipment_id", "timestamp", "failure"],
    value_vars=metric_cols,
    var_name="metric",
    value_name="value",
)

# print(long_df.head(10))



con = duckdb.connect("data/fabcast.duckdb")
con.execute("CREATE OR REPLACE TABLE sensor_readings AS SELECT * FROM long_df")
con.execute("""
    CREATE OR REPLACE TABLE failure_labels AS
    SELECT DISTINCT equipment_id, timestamp, failure FROM df
""")
con.close()



print(f"Loaded {len(long_df):,} sensor readings across {df['equipment_id'].nunique():,} devices")
print(f"Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
