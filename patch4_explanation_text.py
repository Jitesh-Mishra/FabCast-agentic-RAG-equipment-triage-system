with open("app.py") as f:
    content = f.read()

old1 = '''pipeline_card("02", "\\U0001F4DA", "Diagnosis Agent", "RAG over 11 docs, Ollama + Chroma", PURPLE)'''
new1 = '''pipeline_card("02", "\\U0001F4DA", "Diagnosis Agent", "RAG \u2014 local embeddings + Groq LLM", PURPLE)'''

old2 = '''dbox("Diagnosis Agent", "RAG + Ollama LLM", "#c084fc", 190)'''
new2 = '''dbox("Diagnosis Agent", "RAG + Groq LLM", "#c084fc", 190)'''

count1 = content.count(old1)
count2 = content.count(old2)
if count1 != 1 or count2 != 1:
    print(f"FAIL: found {count1} matches for pipeline card text, {count2} for diagram box text (expected 1 each)")
    raise SystemExit(1)

content = content.replace(old1, new1)
content = content.replace(old2, new2)

with open("app.py", "w") as f:
    f.write(content)

print("Explanation text patched successfully.")
print("Groq mentioned:", content.count("Groq"))
print("Ollama mentions remaining:", content.count("Ollama"))
