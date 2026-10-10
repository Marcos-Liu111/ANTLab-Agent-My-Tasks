# -*- coding: utf-8 -*-
"""定位回归/V2 失败的逐字段差异。"""
import copy, json, sys
from pathlib import Path

CB = Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b")
sys.path.insert(0, str(CB))
import challenge, fixed_engine  # noqa: E402
data = json.loads((CB / "data.json").read_text(encoding="utf-8"))
corpus = data["corpus"]

def run(mod, cs, corp):
    eng = getattr(__import__(mod), "Engine")()
    out = {}
    for c in cs:
        if c["reset_before"]:
            eng = getattr(__import__(mod), "Engine")()
        out[c["id"]] = eng.evaluate(copy.deepcopy(c["request"]), corp, copy.deepcopy(c["draft"]))
    return out

def norm(o, extra_drop=()):
    drop = {"request_id", "elapsed_ms", "cache_hit"} | set(extra_drop)
    return {k: v for k, v in o.items() if k not in drop}

base = run("challenge", data["cases"], corpus)
fixd = run("fixed_engine", data["cases"], corpus)

print("=== 回归差异（R01/R05/R06）===")
for cid in ("R01", "R05", "R06"):
    b, f = norm(base[cid]), norm(fixd[cid])
    bk, fk = set(b), set(f)
    if bk != fk or b != f:
        print(f"\n{cid}:")
        print("  字段仅fixed有:", fk - bk, "  仅base有:", bk - fk)
        for k in bk & fk:
            if b[k] != f[k]:
                print(f"  值差异 {k}: base={b[k]!r} fixed={f[k]!r}")
    else:
        print(f"{cid}: 完全一致")

print("\n=== V2 标识变体差异 ===")
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
for cid in sorted(fixd):
    a, b = norm(fixd[cid]), norm(fixd_m[remap(cid)])
    if a != b:
        print(f"\n{cid}:")
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                print(f"  {k}:\n    orig ={a.get(k)!r}\n    remap={b.get(k)!r}")
