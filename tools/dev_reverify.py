# -*- coding: utf-8 -*-
"""强制重跑 dev improved 验证（不跳过已有记录）。"""
import sys, json, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "基础" / "starter"))
import runner  # noqa: E402

conf = runner.load_config(str(REPO / "基础" / "config.local.json"))
GOLD = {"D01": "80%", "D02": "证据不足", "D03": "1.8", "D04": "配置丙"}
results = {}
for cid in ["D01", "D02", "D03", "D04"]:
    for attempt in range(3):
        try:
            r = runner.execute(cid, "R0", "improved", conf, mock=False, dry=False)
            if r["status"] == "ok":
                c = r["response"]["choices"][0]["message"]["content"].strip()
                if c.startswith("```"):
                    c = c.split("\n", 1)[1].rsplit("```", 1)[0].strip() if "```" in c[3:] else c
                try:
                    o = json.loads(c)
                    ans = str(o.get("answer"))
                    hit = "OK" if ans == GOLD[cid] else f"WRONG(gold={GOLD[cid]})"
                    results[cid] = ans
                    print(f"{cid}: ans={ans} cit={o.get('citations')} -> {hit}", flush=True)
                except Exception:
                    results[cid] = "PARSE_FAIL"
                    print(f"{cid}: PARSE_FAIL raw={c[:120]}", flush=True)
                break
            print(f"{cid}: status={r['status']} try={attempt+1}", flush=True)
        except Exception as e:
            print(f"{cid}: {type(e).__name__} try={attempt+1}", flush=True)
            time.sleep(5)

ok = sum(1 for cid, a in results.items() if a == GOLD[cid])
print(f"\n改进后 dev 成绩: {ok}/4")
