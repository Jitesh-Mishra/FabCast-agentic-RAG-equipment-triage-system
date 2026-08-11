with open("src/eval.py") as f:
    content = f.read()

old_prompt = '''DIAGNOSIS_PROMPT = """Use ONLY the context below to explain the likely cause. Cite which
document supports your explanation. If the context doesn't clearly explain this specific
case, say so honestly rather than guessing.

Context:
{context}

Question: {question}

Write a 3-4 sentence answer for a human reviewer."""'''

new_prompt = '''DIAGNOSIS_PROMPT = """Answer the question directly using ONLY the context below. Structure
your response as exactly two parts:
1) A direct 1-2 sentence answer to the question itself, first.
2) Supporting reasoning grounded in the context, citing the source document by name.
If the context doesn't fully address this specific question, say so explicitly instead of
guessing or padding with tangential detail.

Context:
{context}

Question: {question}"""'''

count = content.count(old_prompt)
if count != 1:
    print(f"FAIL: expected exactly 1 match for old prompt, found {count}. No changes made.")
    raise SystemExit(1)

content = content.replace(old_prompt, new_prompt)

with open("src/eval.py", "w") as f:
    f.write(content)

print("Patched successfully.")
print("New prompt present:", "Answer the question directly using ONLY" in content)
print("Old prompt gone:", "Write a 3-4 sentence answer for a human reviewer." not in content)
