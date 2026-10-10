import os, re

repo = r"D:\ANTLab-Agent-Tasks"
emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50]")

found = []
for root, dirs, files in os.walk(repo):
    if ".git" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            p = os.path.join(root, f)
            try:
                txt = open(p, "r", encoding="utf-8").read()
            except Exception:
                continue
            matches = emoji_pattern.findall(txt)
            if matches:
                found.append((os.path.relpath(p, repo), set(matches)))

if found:
    print("Found residual emojis in:")
    for path, syms in found:
        print("  ", path, [hex(ord(s)) for s in syms])
else:
    print("ALL CLEAR: No emoji symbols found in any markdown files.")
