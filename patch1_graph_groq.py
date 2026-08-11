with open("src/graph.py") as f:
    content = f.read()

old = '''from langchain_ollama import ChatOllama

from src.monitor import score_latest
from src.rag import retrieve

llm = ChatOllama(model="llama3.1", temperature=0.2)'''

new = '''import os
from langchain_groq import ChatGroq

from src.monitor import score_latest
from src.rag import retrieve

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, groq_api_key=os.environ.get("GROQ_API_KEY"))'''

count = content.count(old)
if count != 1:
    print(f"FAIL: expected 1 match, found {count}")
    raise SystemExit(1)

content = content.replace(old, new)
with open("src/graph.py", "w") as f:
    f.write(content)

print("graph.py patched successfully.")
print("ChatGroq present:", "ChatGroq" in content)
print("ChatOllama gone:", "ChatOllama" not in content)
