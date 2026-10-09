# -*- coding: utf-8 -*-
"""查看最新 improved 运行的原始响应。"""
import json, glob, os, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
rows = []
for f in glob.glob(str(REPO / "基础" / "runs" / "*.json")):
    r = json.load(open(f, encoding="utf-8"))
    if r.get("variant") == "improved" and r.get("status") == "ok":
        rows.append((os.path.getmtime(f), r))
rows.sort()

for m, r in rows[-4:]:
    t = datetime.datetime.fromtimestamp(m).strftime("%H:%M:%S")
    print("=" * 70)
    print(f"{t} {r['case_id']} {r['condition']} improved")
    print("selected:", r["selected_passage_ids"])
    c = r["response"]["choices"][0]["message"]["content"]
    print("raw content:")
    print(c[:1500])
    print()
