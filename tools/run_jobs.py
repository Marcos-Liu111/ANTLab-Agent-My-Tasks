# -*- coding: utf-8 -*-
"""带重试地跑指定 (case, condition, variant) 列表，跳过已成功记录。"""
import sys, os, json, glob, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "基础" / "starter"))
import runner  # noqa: E402

CONFIG = str(REPO / "基础" / "config.local.json")
JOBS = [  # (case, condition, variant) — 正式配对：评测集 R0 improved x8
    (f"T{i:02d}", "R0", "improved") for i in range(1, 9)
]
MAX_TRY = 3


def done():
    s = set()
    for f in glob.glob(str(REPO / "基础" / "runs" / "*.json")):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if r.get("status") == "ok" and r.get("variant") == "improved":
            s.add((r["case_id"], r["condition"], r["variant"]))
    return s


def main():
    conf = runner.load_config(CONFIG)
    d = done()
    todo = [j for j in JOBS if j not in d]
    print(f"待跑 {len(todo)}/{len(JOBS)}", flush=True)
    failed = []
    for cid, cond, var in todo:
        ok = False
        for a in range(1, MAX_TRY + 1):
            try:
                r = runner.execute(cid, cond, var, conf, mock=False, dry=False)
                if r["status"] == "ok":
                    try:
                        o = json.loads(r["response"]["choices"][0]["message"]["content"])
                        print(f"{cid} {cond} {var} OK  ans={o.get('answer')} cit={o.get('citations')}", flush=True)
                    except Exception:
                        print(f"{cid} {cond} {var} OK  (JSON parse fail)", flush=True)
                    ok = True
                    break
                print(f"{cid} {cond} {var} status={r['status']} try={a}", flush=True)
            except Exception as e:
                print(f"{cid} {cond} {var} {type(e).__name__} try={a}", flush=True)
            time.sleep(5)
        if not ok:
            failed.append((cid, cond, var))
    print("失败:", failed or "无", flush=True)


if __name__ == "__main__":
    main()
