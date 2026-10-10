# -*- coding: utf-8 -*-
"""汇总报告所需的全局统计：调用数、token、按阶段分类。"""
import json, glob
from collections import defaultdict
from pathlib import Path

REPO = Path(r"D:\ANTLab-Agent-Tasks")
runs = []
for f in glob.glob(str(REPO / "基础" / "runs" / "*.json")):
    runs.append(json.load(open(f, encoding="utf-8")))

paid = [r for r in runs if r.get("mode") == "paid"]
dry = [r for r in runs if r.get("mode") == "dry"]
ok = [r for r in paid if r.get("status") == "ok"]
bad = [r for r in paid if r.get("status") != "ok"]

print(f"总记录 {len(runs)}  paid {len(paid)}  dry {len(dry)}  ok {len(ok)}  非ok {len(bad)}")

def tok(rs):
    pt = sum((r.get("usage") or {}).get("prompt_tokens", 0) or 0 for r in rs)
    ct = sum((r.get("usage") or {}).get("completion_tokens", 0) or 0 for r in rs)
    return pt, ct

groups = defaultdict(list)
for r in ok:
    key = (r.get("split"), r.get("variant", "baseline"), r.get("condition"))
    groups[key].append(r)

print("\n分组统计（split, variant, condition）:")
tot_pt = tot_ct = 0
for key in sorted(groups, key=str):
    rs = groups[key]
    pt, ct = tok(rs)
    tot_pt += pt; tot_ct += ct
    print(f"  {str(key):42s} n={len(rs):3d}  prompt={pt:7d} completion={ct:6d}")

print(f"\n付费调用合计: prompt={tot_pt} completion={tot_ct} total={tot_pt+tot_ct}")

# 40 次主请求核对
main = [r for r in ok if r.get("split") == "evaluation"]
print(f"评测集主结果条数: {len(main)}（应=32基线+8改进=40）")
base_eval = [r for r in main if r.get("variant") == "baseline"]
imp_eval = [r for r in main if r.get("variant") == "improved"]
print(f"  基线 {len(base_eval)}  改进 {len(imp_eval)}")

# 非ok记录
if bad:
    print("\n非ok付费记录:")
    for r in bad:
        print("  ", r.get("case_id"), r.get("condition"), r.get("status"), r.get("http_status"))
