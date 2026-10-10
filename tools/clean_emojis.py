import os

repo = r"D:\ANTLab-Agent-Tasks"

replacements = [
    ("✅正确", "正确"),
    ("❌错误", "错误"),
    ("⚠️无法确定", "无法确定"),
    ("✅ 正确", "正确"),
    ("❌ 错误", "错误"),
    ("⚠️ 无法确定", "无法确定"),
    ("✅", "通过"),
    ("❌", "未通过"),
    ("⚠️", "注："),
    ("⭐", ""),
    ("🎉", ""),
    ("📌", ""),
    ("📖", ""),
    ("🌙", ""),
    ("👍", "")
]

updated_files = []

for root, dirs, files in os.walk(repo):
    if ".git" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            path = os.path.join(root, f)
            try:
                content = open(path, "r", encoding="utf-8").read()
            except Exception:
                continue
            new_content = content
            for src, dst in replacements:
                new_content = new_content.replace(src, dst)
            if new_content != content:
                open(path, "w", encoding="utf-8", newline="\n").write(new_content)
                updated_files.append(os.path.relpath(path, repo))

print("Cleaned markdown files:", len(updated_files))
for p in updated_files:
    print(" -", p)
