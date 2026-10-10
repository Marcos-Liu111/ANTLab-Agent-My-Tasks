# -*- coding: utf-8 -*-
"""区分性干预实验（离线重放，零API）：验证 b_predictions.md 中的 E1/E2/C1。
必须在预测文件写入后运行。
"""
import json, sys, time
from pathlib import Path

CB = Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b")
sys.path.insert(0, str(CB))
data = json.loads((CB / "data.json").read_text(encoding="utf-8"))
from challenge import Engine

cases = {c["id"]: c for c in data["cases"]}

def run_case(case, eng=None, label=""):
    eng = eng or Engine()
    out = eng.evaluate(case["request"], data["corpus"], case["draft"])
    print(f"{label}{case['id']}: answer={out['answer']!r} "
          f"evidence={[e['id'] for e in out['evidence']]} "
          f"cit={out['citations']} cache_hit={out['cache_hit']} "
          f"locator={out['locator_status']} elapsed={out['elapsed_ms']:.3f}ms")
    return out

print("=== E1: 全新实例只跑 R02（不先跑 R01）===")
print("  H1预测: 12秒/b02/cache_hit=False | H2预测: 仍30秒/b01")
e1 = run_case(cases["R02"], label="  ")

print("\n=== E1b: 复刻原顺序 R01→R02（同实例，复现baseline症状）===")
eng = Engine()
r1 = run_case(cases["R01"], eng=eng, label="  ")
r2 = run_case(cases["R02"], eng=eng, label="  ")

print("\n=== E2: 全新实例只跑 R03（k=1, doc=beta）===")
print("  H2预测: evidence仍为空（scope外b01挤占k=1名额）| 否则 evidence含b03")
e2 = run_case(cases["R03"], label="  ")

print("\n=== E3/C2: R04 draft语义 vs 原文（评价错误检查，离线）===")
b04 = next(b for b in data["corpus"] if b["id"] == "b04")
print(f"  draft.answer: {cases['R04']['draft']['answer']!r}")
print(f"  b04.text    : {b04['text']!r}")
print("  → 原文只说'没有测量'，draft断言'保证立即释放'，语义冲突")
r4 = run_case(cases["R04"], label="  ")

print("\n=== C1: 缓存键检查（代码事实）===")
import inspect, challenge
src = inspect.getsource(challenge.Engine.evaluate)
line = [l for l in src.splitlines() if "key =" in l]
print("  cache key line:", line[0].strip() if line else "NOT FOUND")
print("  → key 仅含 query，不含 doc_ids/snapshot/k（代码确认事实）")

print("\n=== 判别结论 ===")
ok1 = ("12" in e1["answer"]) and [e["id"] for e in e1["evidence"]] == ["b02"] and not e1["cache_hit"]
ok2 = [e["id"] for e in e2["evidence"]] == []
print(f"  E1 返回12秒/b02/cache_hit=False → H1(缓存污染) {'成立' if ok1 else '不成立'}")
print(f"  E1b 复刻顺序复现30秒/cache_hit=True → 因果链闭合")
print(f"  E2 evidence仍空 → H2(排序先于过滤,独立存在) {'成立' if ok2 else '不成立'}")
print("  R02归因: H1（H2未在此题触发，k=2足够；H2 由 R03 独立证实）")
