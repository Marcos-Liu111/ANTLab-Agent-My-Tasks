# -*- coding: utf-8 -*-
"""B 题检查集：修复后回归 + 2个语义等价变体 + 1个自构造边界。
变体映射与预测先行；全部离线重放。
"""
import copy, json, sys
from pathlib import Path

CB = Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b")
sys.path.insert(0, str(CB))
import challenge, fixed_engine  # noqa: E402
data = json.loads((CB / "data.json").read_text(encoding="utf-8"))
cases = {c["id"]: c for c in data["cases"]}
corpus = data["corpus"]

PREDICTIONS = """
【预测（先于运行写下）】
V1 顺序变体：corpus 全序反转后重跑 7 案 → fixed 输出与 baseline 修复版逐字段一致
   （排序键含 id 字典序与分数，输入顺序不应影响结果）。
V2 标识变体：doc_id 与快照名做保结构映射（alpha→gamma, beta→delta, v1→s1, v2→s2,
   b0x→c0x，全部同步改 request/draft/corpus）→ fixed 输出结构与状态与原版逐字段一致
   （实现只按标识等值比较，不依赖具体字符串）。
B1 自构造边界：answers 引用不存在 id（draft.citations=['ghost']）且答案含无出处数值 →
   fixed: locator=missing, support=not_checked（不越界、不编造 supported）。
"""

def run(mod_name, cs, corp):
    eng = getattr(__import__(mod_name), "Engine")()
    out = {}
    for c in cs:
        if c["reset_before"]:
            eng = getattr(__import__(mod_name), "Engine")()
        out[c["id"]] = eng.evaluate(copy.deepcopy(c["request"]), corp, copy.deepcopy(c["draft"]))
    return out

def norm(o, drop=("request_id", "elapsed_ms", "cache_hit", "support_basis")):
    """支持性披露字段 support_basis 为 fixed 新增，属信息增加而非行为变更，不参与等价比较。"""
    return {k: v for k, v in o.items() if k not in drop}

results = {"predictions": PREDICTIONS, "checks": {}}

# ---- 回归：R01/R05/R06（原本正常的行为） ----
base = run("challenge", data["cases"], corpus)
fixd = run("fixed_engine", data["cases"], corpus)
reg_ok = all(norm(base[c]) == norm(fixd[c]) for c in ("R01", "R05", "R06"))
results["checks"]["regression_R01_R05_R06"] = "PASS" if reg_ok else "FAIL"
print("回归 R01/R05/R06:", results["checks"]["regression_R01_R05_R06"])

# ---- V1 顺序变体 ----
corp_rev = list(reversed(corpus))
fixd_rev = run("fixed_engine", data["cases"], corp_rev)
v1_ok = all(norm(fixd[c]) == norm(fixd_rev[c]) for c in fixd)
results["checks"]["V1_corpus_order"] = "PASS" if v1_ok else "FAIL"
print("V1 语料顺序反转:", results["checks"]["V1_corpus_order"])
if not v1_ok:
    for c in fixd:
        if norm(fixd[c]) != norm(fixd_rev[c]):
            print("  差异:", c, norm(fixd[c]), "vs", norm(fixd_rev[c]))

# ---- V2 标识变体（保结构映射） ----
def remap(x):
    if isinstance(x, str):
        for a, b in [("alpha", "gamma"), ("beta", "delta"), ("v1", "s1"), ("v2", "s2")]:
            x = x.replace(a, b)
        if x.startswith("b0") and len(x) == 3:
            x = "c" + x[1:]
        return x
    if isinstance(x, list):
        return [remap(i) for i in x]
    if isinstance(x, dict):
        return {k: remap(v) for k, v in x.items()}
    return x

cases_m = [remap(copy.deepcopy(c)) for c in data["cases"]]
corp_m = remap(copy.deepcopy(corpus))
fixd_m = run("fixed_engine", cases_m, corp_m)
# 等价比较：原版输出经同一映射后，应与映射输入的输出逐字段一致
v2_ok = all(remap(norm(fixd[c])) == norm(fixd_m[remap(c)]) for c in fixd)
results["checks"]["V2_id_remap"] = "PASS" if v2_ok else "FAIL"
print("V2 标识映射:", results["checks"]["V2_id_remap"])

# ---- B1 自构造边界：幽灵引用 + 无出处数值 ----
ghost_case = copy.deepcopy(cases["R05"])
ghost_case["draft"] = {"answer": "指标为42。",
                       "citations": ["ghost"], "origin": "synthetic_fixture"}
eng = fixed_engine.Engine()
out = eng.evaluate(ghost_case["request"], corpus, ghost_case["draft"])
b1_ok = (out["locator_status"] == "missing" and out["support_status"] == "not_checked"
         and out["status"] == "ok")
results["checks"]["B1_ghost_citation"] = "PASS" if b1_ok else "FAIL"
results["B1_output"] = norm(out)
print("B1 幽灵引用边界:", results["checks"]["B1_ghost_citation"],
      f"locator={out['locator_status']} support={out['support_status']}")
print("  → 未解决边界：该答案的数值无证据，本实现报 not_checked 而非 contradicted（无证据对比对象）")

# ---- 变体与边界的基线对照（修复前后同条件比较） ----
base_rev = run("challenge", data["cases"], corp_rev)
results["baseline_V1_same_output_as_original"] = (
    all(norm(base[c]) == norm(base_rev[c]) for c in base))
print("基线引擎对 V1 是否同样稳定(供对照):", results["baseline_V1_same_output_as_original"])

out_p = Path(r"D:\ANTLab-Agent-Tasks\results\b\regression_variants.json")
out_p.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved:", out_p)
print(PREDICTIONS)
