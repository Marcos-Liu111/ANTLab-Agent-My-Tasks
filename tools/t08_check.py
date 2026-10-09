# -*- coding: utf-8 -*-
"""T08 疑点定性：查看两组证据段原文，判断 K17 与 证据不足 哪个对。"""
import json

CASES = r"D:\ANTLab-Agent-Tasks\基础\data\cases.json"
c = {x["id"]: x for x in json.load(open(CASES, encoding="utf-8"))}["T08"]
print("题目:", c["question"])
print("=" * 70)
for pid in ["P183430", "P223300", "P436140"]:
    p = next(x for x in c["passages"] if x["id"] == pid)
    print(f"\n[{pid}] 来源: {p['source']}")
    print(p["text"][:420])
    print("-" * 60)

# 全文里搜 K17 / selected_snapshot / 快照 出现在哪些段
print("\n关键词分布：")
for p in c["passages"]:
    hits = [k for k in ["K17", "selected_snapshot", "复核表", "快照S19", "迁移批次"] if k in p["text"]]
    if hits:
        print(f"  {p['id']} ({p['source']}): {hits}")
