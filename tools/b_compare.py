# -*- coding: utf-8 -*-
"""修复后全量对照：baseline(challenge) vs fixed(fixed_engine)，同输入同顺序。"""
import json, sys
from pathlib import Path

CB = Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b")
sys.path.insert(0, str(CB))
data = json.loads((CB / "data.json").read_text(encoding="utf-8"))

def run(mod):
    Engine = getattr(__import__(mod), "Engine")
    eng = Engine()
    out = {}
    for case in data["cases"]:
        if case["reset_before"]:
            eng = Engine()
        out[case["id"]] = eng.evaluate(case["request"], data["corpus"], case["draft"])
    return out

base = run("challenge")
fixed = run("fixed_engine")

print(f"{'case':5s} {'baseline':44s} {'fixed':44s}")
print("-" * 96)
for cid in sorted(base):
    b, f = base[cid], fixed[cid]
    bs = f"ans={b['answer'][:12]}|ev={[e['id'] for e in b['evidence']]}|loc={b['locator_status']}|sup={b['support_status']}"
    fs = f"ans={f['answer'][:12]}|ev={[e['id'] for e in f['evidence']]}|loc={f['locator_status']}|sup={f['support_status']}"
    mark = "  <== 变化" if (bs != fs) else ""
    print(f"{cid:5s} {bs:44s} {fs:44s}{mark}")

# 保存修复后结果
out_path = Path(r"D:\ANTLab-Agent-Tasks\results\b\fixed.json")
records = []
eng = None
for case in data["cases"]:
    if case["reset_before"] or eng is None:
        eng = __import__("fixed_engine").Engine()
    records.append({"case_id": case["id"], "input": case,
                    "output": eng.evaluate(case["request"], data["corpus"], case["draft"])})
out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
print("\nsaved:", out_path)
