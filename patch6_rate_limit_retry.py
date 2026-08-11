with open("src/graph.py") as f:
    content = f.read()

old_import = '''import os
from langchain_groq import ChatGroq'''

new_import = '''import os
import time
from langchain_groq import ChatGroq
from groq import RateLimitError'''

old_llm_line = '''llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, groq_api_key=os.environ.get("GROQ_API_KEY"))'''

new_llm_line = '''llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, groq_api_key=os.environ.get("GROQ_API_KEY"))


def call_llm_with_retry(prompt, max_retries=4, base_wait=20):
    """Groq's free tier has a per-minute rate limit. If a burst of flagged
    devices fires several LLM calls at once, wait and retry instead of
    crashing the whole scan."""
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait = base_wait * (attempt + 1)
            print(f"[llm] Rate limited, waiting {wait}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(wait)'''

old_call = "response = llm.invoke(prompt)"
new_call = "response = call_llm_with_retry(prompt)"

count_import = content.count(old_import)
count_llm_line = content.count(old_llm_line)
count_call = content.count(old_call)

if count_import != 1 or count_llm_line != 1 or count_call != 2:
    print(f"FAIL: import matches={count_import} (want 1), llm_line matches={count_llm_line} (want 1), "
          f"call matches={count_call} (want 2)")
    raise SystemExit(1)

content = content.replace(old_import, new_import)
content = content.replace(old_llm_line, new_llm_line)
content = content.replace(old_call, new_call)

with open("src/graph.py", "w") as f:
    f.write(content)

print("Patched successfully.")
print("Retry helper present:", "def call_llm_with_retry" in content)
print("Both call sites updated:", content.count("call_llm_with_retry(prompt)") == 2)
