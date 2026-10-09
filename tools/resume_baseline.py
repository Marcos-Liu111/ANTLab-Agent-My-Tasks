# -*- coding: utf-8 -*-
"""加固版续跑：捕获网络异常、自动重试、失败记录另存。
已完成定义：runs/ 中存在 split=evaluation + mode=paid + status=ok + variant=baseline 的同 (case, cond)。
"""
import sys, os, json, glob, random, time

BASE = r"D:\ANTLab-Agent-Tasks\基础"
sys.path.insert(0, os.path.join(BASE, "starter"))
import runner  # noqa: E402

CONFIG = os.path.join(BASE, "config.local.json")
ORDER_SEED = 20261006
CONDS = ["R0", "R1", "R2", "K"]
MAX_ATTEMPTS = 3          # 单条最多尝试次数（含首次）
RETRY_WAIT = 5            # 重试前等待秒数


def done_set():
    done = set()
    for f in glob.glob(os.path.join(BASE, "runs", "*.json")):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if (r.get("split") == "evaluation" and r.get("mode") == "paid"
                and r.get("status") == "ok" and r.get("variant") == "baseline"):
            done.add((r["case_id"], r["condition"]))
    return done


def main():
    all_jobs = [(c["id"], cond) for c in runner.cases()
                if c["split"] == "evaluation" for cond in CONDS if cond in c["conditions"]]
    random.Random(ORDER_SEED).shuffle(all_jobs)

    done = done_set()
    todo = [j for j in all_jobs if j not in done]
    print(f"总任务 {len(all_jobs)}，已完成 {len(done & set(all_jobs))}，待跑 {len(todo)}", flush=True)
    if not todo:
        print("无待跑任务")
        return

    conf = runner.load_config(CONFIG)
    ok, failed = 0, []

    for i, (cid, cond) in enumerate(todo, 1):
        last_err = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                r = runner.execute(cid, cond, "baseline", conf, mock=False, dry=False)
                if r["status"] == "ok":
                    ok += 1
                    print(f"[{i}/{len(todo)}] {cid} {cond} OK "
                          f"({r['elapsed_seconds']:.1f}s) attempt={attempt}", flush=True)
                    last_err = None
                    break
                # 非 ok 状态（http_error / transport_error）也算失败，重试
                last_err = f"status={r['status']} http={r.get('http_status')} err={r.get('error')}"
                print(f"[{i}/{len(todo)}] {cid} {cond} {last_err} attempt={attempt}", flush=True)
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                print(f"[{i}/{len(todo)}] {cid} {cond} EXCEPTION {last_err} attempt={attempt}", flush=True)
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_WAIT)
        if last_err is not None:
            failed.append({"case": cid, "cond": cond, "error": last_err})

    print(f"\n完成：成功 {ok}/{len(todo)}", flush=True)
    if failed:
        out = os.path.join(BASE, "runs", "_failed_jobs.json")
        json.dump(failed, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"失败 {len(failed)} 条，已记录到 {out}")
        for x in failed:
            print("  ", x)


if __name__ == "__main__":
    main()
