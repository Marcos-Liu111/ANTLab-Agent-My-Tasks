# -*- coding: utf-8 -*-
"""打印指定题目的完整原文（题目 + 全部7段）。"""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
cases = {c["id"]: c for c in json.load(open(str(REPO / "基础" / "data" / "cases.json"), encoding="utf-8"))}

cid = sys.argv[1] if len(sys.argv) > 1 else "T05"
c = cases[cid]
print(f"题目（{cid}）：{c['question']}")
print("=" * 80)
for i, p in enumerate(c["passages"], 1):
    print(f"\n[{i}] {p['id']}  来源: {p['source']}")
    print("-" * 70)
    print(p["text"])
