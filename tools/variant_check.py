# -*- coding: utf-8 -*-
"""第六步变体检查（不调用模型）：
对 improve() 做段落顺序打乱与ID重映射扰动，验证它按内容分档而非按输入位置工作。

预测（写在验证之前，见 PREDICTION 注释）：
  P1: 打乱输入顺序 100 次，improve() 的输出分档序列（tier序列）完全相同；
  P2: 重映射 ID（P→Q）后分档结构不变（improve 不读 ID）；
  P3: 输出是输入的稳定排序子集（只重排，不增删不修改段落）。
任何一条不成立 → 说明 improve 依赖位置或 ID → 预测被推翻。
"""
import json, random, sys, copy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "基础" / "starter"))
import student  # noqa: E402

PREDICTION = """
预测记录（运行前写下，2026-10-09 20:0x）：
  P1 打乱顺序不影响分档输出；P2 重映射ID不影响分档；P3 只重排不修改。
"""

cases = {c["id"]: c for c in json.load(open(str(REPO / "基础" / "data" / "cases.json"), encoding="utf-8"))}
case_ids = [c["id"] for c in cases.values() if c.get("split") == "evaluation"]

def tiers(order):
    """按 improve 同款分档标注返回 tier 序列（独立复算，不复用 student.improve 内部）。"""
    out = []
    for p in order:
        t = p["text"]
        head = t[:80]
        if "复核补页" in t or "规则" in head:
            out.append(0)
        elif "的记录：" in t and not any(k in t for k in ("迁移批次", "压力组", "探索组")):
            out.append(1)
        elif any(k in t for k in ("迁移批次", "压力组", "探索组", "岫光")):
            out.append(3)
        else:
            out.append(2)
    return out

print(PREDICTION)
rng = random.Random(20261009)
p1 = p2 = p3 = True

for cid in case_ids:
    ps = copy.deepcopy(cases[cid]["passages"])
    # 基准输出
    base = student.improve(cases[cid]["question"], copy.deepcopy(ps))
    base_t = tiers(base)

    # P1: 100 次乱序输入
    for _ in range(100):
        shuf = rng.sample(copy.deepcopy(ps), len(ps))
        got = student.improve(cases[cid]["question"], shuf)
        if tiers(got) != base_t:
            p1 = False
            print(f"P1 FAIL {cid}: tier序列随输入顺序变化")
            break
        # P3: 只重排不修改
        if sorted(p["id"] for p in got) != sorted(p["id"] for p in ps):
            p3 = False
            print(f"P3 FAIL {cid}: 段落集合变化")
        for a, b in zip(sorted(got, key=lambda x: x["id"]), sorted(ps, key=lambda x: x["id"])):
            if a != b:
                p3 = False
                print(f"P3 FAIL {cid}: 段落内容被修改 {a['id']}")

    # P2: ID 重映射 P→Q
    remapped = []
    for p in copy.deepcopy(ps):
        p["id"] = p["id"].replace("P", "Q", 1)
        remapped.append(p)
    got2 = student.improve(cases[cid]["question"], remapped)
    if [p["id"].replace("Q", "P", 1) for p in got2] != [p["id"] for p in base]:
        p2 = False
        print(f"P2 FAIL {cid}: 重映射ID后输出选择变化")

print(f"P1 乱序稳定: {'PASS' if p1 else 'FAIL'}  "
      f"P2 ID重映射: {'PASS' if p2 else 'FAIL'}  "
      f"P3 只重排: {'PASS' if p3 else 'FAIL'}")
print("结论:", "预测全部成立，improve 按内容分档工作，与输入位置/ID 无关"
      if (p1 and p2 and p3) else "存在预测被推翻项，见上")
