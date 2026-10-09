# -*- coding: utf-8 -*-
"""深度分析：
1. T08 顺序异常：对比 R0/R1/R2 实际输入段落与输出差异（离线，不调用API）
2. 引用一致性：同题跨条件的引用集合是否稳定
3. K 条件丢失了哪些段（与 R0 输入对比）
4. 耗时异常检测
"""
import json, glob, os, itertools
from collections import defaultdict

RUNS = r"D:\ANTLab-Agent-Tasks\基础\runs"
CASES = r"D:\ANTLab-Agent-Tasks\基础\data\cases.json"

runs = {}
for f in glob.glob(os.path.join(RUNS, "*.json")):
    r = json.load(open(f, encoding="utf-8"))
    if r.get("split") != "evaluation" or r.get("mode") != "paid":
        continue
    key = (r["case_id"], r["condition"])
    runs[key] = r

cases = {c["id"]: c for c in json.load(open(CASES, encoding="utf-8"))}


def answer_of(r):
    try:
        return json.loads(r["response"]["choices"][0]["message"]["content"])
    except Exception:
        return None


print("=" * 70)
print("1. T08 顺序异常深挖")
print("=" * 70)
for cond in ["R0", "R1", "R2", "K"]:
    r = runs[("T08", cond)]
    a = answer_of(r)
    print(f"\n--- T08 / {cond} ---")
    print("  输入段落顺序:", r["selected_passage_ids"])
    print("  输出:", a)
    # 找到 R0 独有的第三段 P436140 内容摘要
c = cases["T08"]
print("\n题目:", c["question"])
print("\nR0/R1/R2 三条件输入段落ID集合是否相同:",
      set(runs[("T08", "R0")]["selected_passage_ids"]) ==
      set(runs[("T08", "R1")]["selected_passage_ids"]) ==
      set(runs[("T08", "R2")]["selected_passage_ids"]))
print("R0 实际顺序:", runs[("T08", "R0")]["selected_passage_ids"])
print("R1 实际顺序:", runs[("T08", "R1")]["selected_passage_ids"])
print("R2 实际顺序:", runs[("T08", "R2")]["selected_passage_ids"])

# 输出 R0 引用但 R1/R2 未引用的段
r0 = answer_of(runs[("T08", "R0")])
r1 = answer_of(runs[("T08", "R1")])
extra = set(r0["citations"]) - set(r1["citations"])
print("\nR0 多引用的段:", extra)
byid = {p["id"]: p for p in c["passages"]}
for pid in extra:
    t = byid[pid]["text"]
    print(f"\n  [{pid}] {byid[pid]['source']}")
    print("  ", t[:300])

print("\n" + "=" * 70)
print("2. 各题跨条件引用稳定性（R0/R1/R2 集合对比）")
print("=" * 70)
for cid in sorted({k[0] for k in runs}):
    sets = {}
    for cond in ["R0", "R1", "R2", "K"]:
        a = answer_of(runs[(cid, cond)])
        sets[cond] = frozenset(a["citations"]) if a else None
    full_same = sets["R0"] == sets["R1"] == sets["R2"]
    print(f"{cid}: R0/R1/R2引用集合一致={'是' if full_same else '否'}  K与R0交集={len(sets['K'] & sets['R0'])}/{len(sets['R0'])}")

print("\n" + "=" * 70)
print("3. K 条件相比 R0 少了哪些段")
print("=" * 70)
for cid in sorted({k[0] for k in runs}):
    r0_ids = set(runs[(cid, "R0")]["selected_passage_ids"])
    k_ids = set(runs[(cid, "K")]["selected_passage_ids"])
    a_r0 = answer_of(runs[(cid, "R0")])
    a_k = answer_of(runs[(cid, "K")])
    lost_needed = set(a_r0["citations"]) - k_ids  # R0引用但K没给的段
    print(f"{cid}: K给的={sorted(k_ids)} | R0答={a_r0['answer']} K答={a_k['answer']} | "
          f"K缺失R0所用证据段={sorted(lost_needed) or '无'}")

print("\n" + "=" * 70)
print("4. 耗时异常（>15s 或 <3s）")
print("=" * 70)
for (cid, cond), r in sorted(runs.items()):
    e = r.get("elapsed_seconds") or 0
    if e > 15 or e < 3:
        print(f"  {cid}/{cond}: {e:.2f}s  prompt={r['usage']['prompt_tokens']} completion={r['usage']['completion_tokens']}")

print("\n" + "=" * 70)
print("5. token 用量总计")
print("=" * 70)
pt = sum(r["usage"]["prompt_tokens"] for r in runs.values())
ct = sum(r["usage"]["completion_tokens"] for r in runs.values())
print(f"  prompt={pt}  completion={ct}  total={pt+ct}")
