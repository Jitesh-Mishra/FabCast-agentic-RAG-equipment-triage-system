with open("app.py") as f:
    content = f.read()

lines = content.splitlines(keepends=True)
already_has_import = any(line.strip() == "import time" for line in lines)

if already_has_import:
    print("`import time` already present as its own line -- something else is wrong. No changes made.")
else:
    content = "import time\n" + content
    with open("app.py", "w") as f:
        f.write(content)
    print("Added 'import time' to the top of app.py.")

with open("app.py") as f:
    final = f.read()
print("Verification -- 'import time' line present:", any(l.strip() == "import time" for l in final.splitlines()))
print("time.sleep(2) still present:", "time.sleep(2)" in final)
