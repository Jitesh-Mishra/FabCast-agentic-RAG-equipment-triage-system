with open("app.py") as f:
    content = f.read()

old = '''                    graph.invoke({"equipment_id": d}, config=config)
                    st.session_state.pending_tickets[config["configurable"]["thread_id"]] = {
                        "device": d, "config": config,
                        "scan_date": st.session_state.current_date.date(),
                        "onset_date": onset.get("onset_date"),
                    }'''

new = '''                    graph.invoke({"equipment_id": d}, config=config)
                    time.sleep(2)  # brief pacing so a burst of flagged devices doesn't trip Groq's per-minute rate limit
                    st.session_state.pending_tickets[config["configurable"]["thread_id"]] = {
                        "device": d, "config": config,
                        "scan_date": st.session_state.current_date.date(),
                        "onset_date": onset.get("onset_date"),
                    }'''

count = content.count(old)
if count != 1:
    print(f"FAIL: expected 1 match, found {count}")
    raise SystemExit(1)

content = content.replace(old, new)

if "import time" not in content:
    content = content.replace("import streamlit as st\n", "import streamlit as st\nimport time\n", 1)

with open("app.py", "w") as f:
    f.write(content)

print("Patched successfully.")
print("time.sleep(2) present:", "time.sleep(2)" in content)
print("time import present:", "import time" in content)
