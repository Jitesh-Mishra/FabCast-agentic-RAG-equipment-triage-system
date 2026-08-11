with open("app.py") as f:
    content = f.read()

old = '''import streamlit as st
import duckdb
import pandas as pd
from datetime import timedelta
from src.graph import graph
from src.monitor import score_latest, score_as_of, get_issue_onset'''

new = '''import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()  # local dev: reads GROQ_API_KEY from a .env file if present
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass  # no secrets.toml locally -- fine, .env above already covered it

import duckdb
import pandas as pd
from datetime import timedelta
from src.graph import graph
from src.monitor import score_latest, score_as_of, get_issue_onset'''

count = content.count(old)
if count != 1:
    print(f"FAIL: expected 1 match, found {count}")
    raise SystemExit(1)

content = content.replace(old, new)
with open("app.py", "w") as f:
    f.write(content)

print("app.py patched successfully.")
print("dotenv bridge present:", "load_dotenv()" in content)
