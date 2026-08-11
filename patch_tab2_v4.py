with open("app.py") as f:
    content = f.read()

old = "    st.markdown(diagram_html, unsafe_allow_html=True)"
new = (
    "    diagram_html = \"\\n\".join(line.strip() for line in diagram_html.strip().split(\"\\n\"))\n"
    "    st.markdown(diagram_html, unsafe_allow_html=True)"
)

count = content.count(old)
if count != 1:
    print(f"FAIL: expected exactly 1 match, found {count}. No changes made.")
    raise SystemExit(1)

content = content.replace(old, new)

with open("app.py", "w") as f:
    f.write(content)

print("Patched successfully. Verifying:")
print("dedent line present:", 'line.strip() for line in diagram_html' in content)
