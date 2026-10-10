# -*- coding: utf-8 -*-
"""查看完整 corpus 并跑 baseline，对照 spec 找症状。"""
import json, sys
from pathlib import Path

CB = Path(r"D:\ANTLab-Agent-Tasks\进阶\challenge_b")
sys.path.insert(0, str(CB))
data = json.loads((CB / "data.json").read_text(encoding="utf-8"))

print("=== 完整 corpus ===")
for b in data["corpus"]:
    print(json.dumps(b, ensure_ascii=False))

print("\n=== 运行 challenge:Engine ===")
from challenge import Engine
eng = Engine()
for case in data["cases"]:
    if case["reset_before"]:
        eng = Engine()
    out = eng.evaluate(case["request"], data["corpus"], case["draft"])
    print(f"\n{case['id']} req={case['request']}")
    print(f"  answer={out['answer']!r}")
    print(f"  citations={out['citations']}")
    print(f"  evidence_ids={[e['id'] for e in out['evidence']]}")
    print(f"  locator={out['locator_status']} support={out['support_status']} "
          f"src={out['judgment_source']} cache_hit={out['cache_hit']} status={out['status']}")
