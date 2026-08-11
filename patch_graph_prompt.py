with open("src/graph.py") as f:
    content = f.read()

old_prompt = '''    prompt = f"""You are a maintenance triage assistant. An automated monitor flagged
equipment {state['equipment_id']} as at-risk (triggered by: {anomaly.get('triggered_by')}).

Use ONLY the context below to explain the likely cause. Cite which document
supports your explanation. If the context doesn't clearly explain this
specific case, say so honestly rather than guessing.

Context:
{context}

Write a 3-4 sentence diagnosis for a human reviewer."""'''

new_prompt = '''    prompt = f"""You are a maintenance triage assistant. An automated monitor flagged
equipment {state['equipment_id']} as at-risk (triggered by: {anomaly.get('triggered_by')}).

Answer directly using ONLY the context below. Structure your response as exactly two parts:
1) A direct 1-2 sentence diagnosis, first.
2) Supporting reasoning grounded in the context, citing the source document by name.
If the context doesn't fully explain this specific case, say so explicitly instead of
guessing or padding with tangential detail.

Context:
{context}"""'''

count = content.count(old_prompt)
if count != 1:
    print(f"FAIL: expected exactly 1 match, found {count}. No changes made.")
    raise SystemExit(1)

content = content.replace(old_prompt, new_prompt)

with open("src/graph.py", "w") as f:
    f.write(content)

print("Patched successfully.")
print("New prompt present:", "Answer directly using ONLY the context below" in content)
print("Old prompt gone:", "Write a 3-4 sentence diagnosis for a human reviewer." not in content)
