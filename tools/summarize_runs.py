# -*- coding: utf-8 -*-
"""汇总评测集基线结果：逐题表 + 汇总统计。
输出 results/baseline_summary.md 与 results/baseline_runs.csv。
复算：python tools/summarize_runs.py
"""
import json, glob, os, csv, datetime, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = str(REPO / "基础" / "runs")
OUT = str(REPO / "results")
os.makedirs(OUT, exist_ok=True)

rows = []
for f in glob.glob(os.path.join(RUNS, "*.json")):
    r = json.load(open(f, encoding="utf-8"))
    if r.get("split") != "evaluation" or r.get("mode") != "paid":
        continue
    content = None
    parsed = None
    if r.get("status") == "ok":
        try:
            content = r["response"]["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception:
            parsed = None
    rows.append({
        "run_id": r["run_id"],
        "case": r["case_id"],
        "cond": r["condition"],
        "variant": r.get("variant", "baseline"),
        "status": r.get("status"),
        "answer": (parsed or {}).get("answer") if parsed else None,
        "citations": (parsed or {}).get("citations") if parsed else None,
        "json_ok": parsed is not None,
        "citations_in_input": (
            None if not parsed else set(parsed.get("citations", [])) <= set(r.get("selected_passage_ids", []))
        ),
        "elapsed": r.get("elapsed_seconds"),
        "prompt_tokens": (r.get("usage") or {}).get("prompt_tokens"),
        "completion_tokens": (r.get("usage") or {}).get("completion_tokens"),
        "selected": r.get("selected_passage_ids"),
    })

rows.sort(key=lambda x: (x["case"], {"R0": 0, "R1": 1, "R2": 2, "K": 3}.get(x["cond"], 9)))

csv_path = os.path.join(OUT, "baseline_runs.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["run_id", "case", "cond", "variant", "status", "answer",
                "citations", "json_ok", "citations_in_input", "elapsed_s",
                "prompt_tokens", "completion_tokens", "selected_ids"])
    for x in rows:
        w.writerow([x["run_id"], x["case"], x["cond"], x["variant"], x["status"],
                    x["answer"], "|".join(x["citations"] or []), x["json_ok"],
                    x["citations_in_input"] if x["citations_in_input"] is not None else "",
                    round(x["elapsed"], 2) if x["elapsed"] else "",
                    x["prompt_tokens"] or "", x["completion_tokens"] or "",
                    "|".join(x["selected"] or [])])

md = []
md.append("# 基线运行汇总（评测集 T01–T08 × R0/R1/R2/K）\n")
md.append(f"- 生成时间：{datetime.datetime.now().isoformat(timespec='seconds')}")
md.append(f"- 记录条数：{len(rows)}")
md.append("- 汇总文件：`results/baseline_runs.csv`")
md.append("- 全部原始记录：`基础/runs/`（每条约含实际 messages、原始响应、usage、耗时）\n")

md.append("## 逐题结果\n")
md.append("| 题号 | 条件 | 状态 | 答案 | 引用 | 引用均来自输入 | 耗时(s) |")
md.append("|---|---|---|---|---|---|---|")
for x in rows:
    cit = "、".join(x["citations"] or [])
    cin = "" if x["citations_in_input"] is None else ("是" if x["citations_in_input"] else "**否**")
    md.append(f"| {x['case']} | {x['cond']} | {x['status']} | {x['answer']} | {cit} | {cin} | "
              f"{round(x['elapsed'],2) if x['elapsed'] else ''} |")

ok = [x for x in rows if x["status"] == "ok"]
md.append("\n## 汇总统计\n")
md.append(f"- 成功 / 总数：{len(ok)} / {len(rows)}")
md.append(f"- JSON 可解析：{sum(1 for x in ok if x['json_ok'])} / {len(ok)}")
md.append(f"- 引用全部来自输入：{sum(1 for x in ok if x['citations_in_input'])} / {len(ok)}")
md.append(f"- 回答“证据不足”的次数：{sum(1 for x in ok if (x['answer'] or '').strip() == '证据不足')}")
if ok:
    el = sorted(x["elapsed"] for x in ok if x["elapsed"])
    md.append(f"- 客户端耗时：中位数 {el[len(el)//2]:.2f}s，最小 {el[0]:.2f}s，最大 {el[-1]:.2f}s")

md.append("\n## 按条件分布\n")
md.append("| 条件 | 成功 | 证据不足 | 中位耗时 |")
md.append("|---|---|---|---|")
for cond in ["R0", "R1", "R2", "K"]:
    sub = [x for x in ok if x["cond"] == cond]
    if not sub:
        continue
    el = sorted(x["elapsed"] for x in sub if x["elapsed"])
    med = f"{el[len(el)//2]:.2f}s" if el else ""
    md.append(f"| {cond} | {len(sub)} | {sum(1 for x in sub if (x['answer'] or '').strip()=='证据不足')} | {med} |")

with open(os.path.join(OUT, "baseline_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print(f"rows={len(rows)}  ok={len(ok)}")
print(f"written: {csv_path}")
print(f"written: {os.path.join(OUT, 'baseline_summary.md')}")
