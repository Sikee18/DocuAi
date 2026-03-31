import os

# Recursive scan for all relevant text-based files
files_to_check = []
for root, dirs, files in os.walk("."):
    # Skip library and build folders
    if any(p in root for p in ["venv", ".web", "node_modules", ".git", "__pycache__"]):
        continue
    for file in files:
        if file.endswith((".py", ".env", ".txt", ".json", ".config")):
            files_to_check.append(os.path.join(root, file))

print(f"Checking {len(files_to_check)} files...")

for file_path in files_to_check:
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            # Try decoding as standard UTF-8
            content.decode("utf-8")
    except UnicodeDecodeError:
        print(f"FAIL: {file_path} - Found non-UTF8 characters. Sanitizing...")
        # Fix by re-saving as pure UTF-8, dropping bad bytes
        sanitized = content.decode("utf-8", "ignore")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sanitized)
        print(f"FIXED: {file_path}")
    except Exception as e:
        pass
