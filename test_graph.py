import duckdb
from src.monitor import score_latest
from src.graph import graph

con = duckdb.connect("data/fabcast.duckdb", read_only=True)
devices = con.sql("SELECT DISTINCT equipment_id FROM sensor_readings").df()["equipment_id"].tolist()
con.close()

flagged_device = None
for d in devices:
    result = score_latest(d)
    if result["is_anomaly"]:
        flagged_device = d
        break

if not flagged_device:
    print("No anomalous device found in a quick scan — widen the search.")
else:
    print(f"\nRunning full graph on flagged device: {flagged_device}\n")
    config = {"configurable": {"thread_id": flagged_device}}
    graph.invoke({"equipment_id": flagged_device}, config=config)

    state = graph.get_state(config).values
    print("\n--- DIAGNOSIS ---")
    print(state.get("diagnosis"))
    print("\n--- CITATIONS ---")
    print(state.get("citations"))
    print("\n--- TICKET DRAFT ---")
    print(state.get("ticket_draft"))
    print("\n(Graph is now paused at the human-approval interrupt.)")
