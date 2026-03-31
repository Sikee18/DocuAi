import os

old_url = "localhost:8000"
new_url = "localhost:8000"

for root, dirs, files in os.walk("."):
    if any(p in root for p in ["venv", "node_modules", ".git", "__pycache__"]):
        continue
    for file in files:
        if file.endswith((".py", ".env", ".js", ".json", ".config", ".ts", ".tsx")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if old_url in content:
                    print(f"FIXING: {file_path}")
                    new_content = content.replace(old_url, new_url)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
            except Exception:
                pass
print("Purge Complete.")
