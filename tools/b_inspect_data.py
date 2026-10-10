# -*- coding: utf-8 -*-
"""查看 challenge_b/data.json 结构与用例。"""
import json
from pathlib import Path

d = json.loads(Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b\data.json").read_text(encoding="utf-8"))
print("keys:", list(d.keys()))
print("corpus size:", len(d["corpus"]))
print("\n--- corpus 前2条 ---")
for b in d["corpus"][:2]:
    print(json.dumps(b, ensure_ascii=False)[:300])
print("\ncases:", len(d["cases"]))
for c in d["cases"]:
    print("\n=", c["id"], "reset_before =", c["reset_before"])
    print("  request:", json.dumps(c["request"], ensure_ascii=False))
    print("  draft:", json.dumps(c["draft"], ensure_ascii=False)[:300])
