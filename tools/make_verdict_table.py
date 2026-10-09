# -*- coding: utf-8 -*-
"""生成逐题核对表：题目 + 各条件答案 + 引用段落原文，供人工判断。
输出 results/verdict_per_case.md（人工判断栏留空，由本人填写）。
复算：python tools/make_verdict_table.py
"""
import json, glob, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "基础" / "runs"
CASES = REPO / "基础" / "data" / "cases.json"
OUT = REPO / "results" / "verdict_per_case.md"

cases = {c["id"]: c for c in json.load(open(CASES, encoding="utf-8"))}

# 载入所有评测 paid 记录
runs = {}
for f in glob.glob(str(RUNS / "*.json")):
    r = json.load(open(f, encoding="utf-8"))
    if r.get("split") == "evaluation" and r.get("mode") == "paid":
        runs[(r["case_id"], r["condition"])] = r


def ans_cit(r):
    try:
        o = json.loads(r["response"]["choices"][0]["message"]["content"])
        return o.get("answer"), o.get("citations", [])
    except Exception:
        return "<解析失败>", []


lines = ["# 逐题核对表（第四步：人工判断）", ""]
lines.append("> **填写说明（本人逐题完成）**")
lines.append("> 1. 先只看题目与引用原文，自己写出**你认为的正确答案**（心里或写入\"我的答案\"栏）。")
lines.append("> 2. 再对照模型 4 个条件的答案，逐格判定：对 / 错 / 无法确定。")
lines.append("> 3. 同时核对：引用段落的原文是否**真的支持**该答案（语义支持，不是关键词命中）。")
lines.append("> 4. 评测题无公开答案，你的判断依据 = 题目 + 段落原文 + 四元组匹配规则。")
lines.append("> 5. 分母口径：32 次首次有效尝试全部计入；本表按题×条件呈现。")
lines.append("")
lines.append("| 题号 | 条件 | 模型答案 | 引用 | 引用均来自输入 | 耗时(s) | 你的判断(对/错/?) | 引用支持?(是/否/?) |")
lines.append("|---|---|---|---|---|---|---|---|")

eval_ids = sorted(c for c in cases if any(k[0] == c for k in runs))
for cid in eval_ids:
    for cond in ["R0", "R1", "R2", "K"]:
        r = runs[(cid, cond)]
        a, cits = ans_cit(r)
        cin = set(cits) <= set(r["selected_passage_ids"])
        lines.append(f"| {cid} | {cond} | {a} | {'、'.join(cits)} | {'是' if cin else '否'} | "
                     f"{r['elapsed_seconds']:.1f} | | |")

lines.append("")
lines.append("---")
lines.append("")

for cid in eval_ids:
    c = cases[cid]
    byid = {p["id"]: p for p in c["passages"]}
    r0 = runs[(cid, "R0")]
    a0, c0 = ans_cit(r0)
    lines.append(f"## {cid}")
    lines.append("")
    lines.append(f"**题目**：{c['question']}")
    lines.append("")
    lines.append(f"**各条件答案**：R0=`{a0}` / R1=`{ans_cit(runs[(cid,'R1')])[0]}` / "
                 f"R2=`{ans_cit(runs[(cid,'R2')])[0]}` / K=`{ans_cit(runs[(cid,'K')])[0]}`")
    lines.append("")
    # 收集所有条件引用的段（展示原文）
    all_cits = []
    for cond in ["R0", "R1", "R2", "K"]:
        for p in ans_cit(runs[(cid, cond)])[1]:
            if p not in all_cits:
                all_cits.append(p)
    lines.append(f"**被引用段落原文**（共 {len(all_cits)} 段）：")
    lines.append("")
    for pid in all_cits:
        p = byid.get(pid)
        if not p:
            lines.append(f"- **{pid}**（注意：未在本题段落中找到！）")
            continue
        owners = [cond for cond in ["R0", "R1", "R2", "K"] if pid in ans_cit(runs[(cid, cond)])[1]]
        lines.append(f"### {pid}（来源：{p['source']}；被 {'/'.join(owners)} 引用）")
        lines.append("")
        lines.append("> " + p["text"].replace("\n", "\n> "))
        lines.append("")
    # 也列出未被引用的段（防止漏看陷阱段）
    uncited = [pid for pid in byid if pid not in all_cits]
    if uncited:
        lines.append(f"**未被任何条件引用的段**：{'、'.join(sorted(uncited))}")
        lines.append("")
        for pid in sorted(uncited):
            p = byid[pid]
            lines.append(f"<details><summary>{pid}（{p['source']}）原文</summary>")
            lines.append("")
            lines.append(p["text"])
            lines.append("")
            lines.append("</details>")
        lines.append("")
    lines.append("**我的答案**：＿＿＿＿＿＿＿＿")
    lines.append("")
    lines.append("**判断依据/备注**：＿＿＿＿＿＿＿＿")
    lines.append("")
    lines.append("---")
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"written: {OUT}")
print(f"questions: {len(cases)}, verdict rows: {len(cases)*4}")
