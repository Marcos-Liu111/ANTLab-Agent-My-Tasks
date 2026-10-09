# -*- coding: utf-8 -*-
"""复测：D01 R0 improved 连跑 N 次，检查劣化是否可复现。"""
import sys, json, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "基础" / "starter"))
import runner  # noqa: E402

conf = runner.load_config(str(REPO / "基础" / "config.local.json"))
for i in range(1, 3):
    for attempt in range(3):
        try:
            r = runner.execute("D01", "R0", "improved", conf, mock=False, dry=False)
            if r["status"] == "ok":
                c = r["response"]["choices"][0]["message"]["content"]
                try:
                    o = json.loads(c)
                    print(f"[{i}] ans={o.get('answer')} cit={o.get('citations')} raw={c[:80]}", flush=True)
                except Exception:
                    print(f"[{i}] PARSE FAIL raw={c[:200]}", flush=True)
                break
            print(f"[{i}] status={r['status']}", flush=True)
        except Exception as e:
            print(f"[{i}] {type(e).__name__} attempt={attempt}", flush=True)
            time.sleep(5)
