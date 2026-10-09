# -*- coding: utf-8 -*-
"""生成逐题核对表：题目 + 各条件答案 + R0引用段落原文 + 人工判断栏。
输出 results/verdict_per_case.md
用法：python tools/gen_verdict_sheet.py
"""
import json, glob, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = str(REPO / "基础" / "runs")
CASES = str(REPO / "基础" / "data" / "cases.json")

# 加载运行结果
runs = {}
for f in glob.glob(os.path.join(RUNS, "*.json")):
    r = json.load(open(f, encoding="utf-8"))
    if r.get("split") == "evaluation" and r.get("mode") == "paid" and r.get("variant") == "baseline":
        runs[(r["case_id"], r["condition"])] = r

cases = {c["id"]: c for c in json.load(open(CASES, encoding="utf-8"))}


def ans(r):
    try:
        o = json.loads(r["response"]["choices"][0]["message"]["content"])
        return o.get("answer"), o.get("citations", [])
    except Exception:
        return None, []


out = []
out.append("# 逐题核对表（第四步 · 人工判断）")
out.append("")
out.append("> **使用方法**：对每个 T 题，先读题目与下方 R0 引用段落原文，")
out.append("> 自己得出正确答案，再对照模型输出判定。评测题无公开答案，判定即你本人的核验结论。")
out.append("> 判定符号：✅正确 / ❌错误 / ⚠️无法确定（说明原因）。")
out.append(">")
out.append("> 引用核对三问：①引用ID是否来自实际输入 ②引用原文是否支持结论 ③答案格式是否符合题目要求。")
out.append("")
out.append("---")

for cid in sorted(cases):
    c = cases[cid]
    if c.get("split") != "evaluation":
        continue
    out.append("")
    out.append(f"## {cid}")
    out.append("")
    out.append(f"**题目**：{c['question']}")
    out.append("")
    out.append("### 各条件输出")
    out.append("")
    out.append("| 条件 | 答案 | 引用 | 耗时(s) |")
    out.append("|---|---|---|---|")
    for cond in ["R0", "R1", "R2", "K"]:
        r = runs[(cid, cond)]
        a, cits = ans(r)
        out.append(f"| {cond} | {a} | {'、'.join(cits)} | {r['elapsed_seconds']:.2f} |")
    out.append("")
    out.append("### R0 引用段落原文（核对材料）")
    out.append("")
    a0, cits0 = ans(runs[(cid, "R0")])
    byid = {p["id"]: p for p in c["passages"]}
    for pid in cits0:
        p = byid.get(pid)
        if not p:
            continue
        out.append(f"**[{pid}] {p['source']}**")
        out.append("")
        out.append("> " + p["text"])
        out.append("")
    # K 额外引用的段（可能与R0不同）
    ak, citsk = ans(runs[(cid, "K")])
    extra_k = set(citsk) - set(cits0)
    if extra_k:
        out.append("### K 条件额外引用的段落（词法检索提供，非 R0 证据）")
        out.append("")
        for pid in sorted(extra_k):
            p = byid.get(pid)
            if p:
                out.append(f"**[{pid}] {p['source']}**")
                out.append("")
                out.append("> " + p["text"])
                out.append("")
    out.append("### 本人判断")
    out.append("")
    out.append("- 正确答案（本人核对原文后填写）：")
    out.append("- R0 判定（✅/❌/⚠️）：")
    out.append("- R1 判定：")
    out.append("- R2 判定：")
    out.append("- K 判定：")
    out.append("- 引用是否支持结论：")
    out.append("- 备注/调整依据：")
    out.append("")
    out.append("---")

dst = REPO / "results" / "verdict_per_case.md"
dst.write_text("\n".join(out) + "\n", encoding="utf-8")
print("written:", dst)
print("chars:", len("\n".join(out)))
