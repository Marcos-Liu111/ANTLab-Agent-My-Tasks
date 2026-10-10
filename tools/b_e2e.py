# -*- coding: utf-8 -*-
"""端到端测试：/api/run_both R01→R02 顺序（复现修复前后差异）。"""
import json, urllib.request

def post(payload):
    req = urllib.request.Request("http://127.0.0.1:8766/api/run_both",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

# R01（清空状态）
d1 = post({"case_id": "R01", "reset": True})
print("R01 baseline:", d1["baseline"]["answer"], d1["baseline"]["evidence"][0]["id"])
print("R01 fixed   :", d1["fixed"]["answer"], d1["fixed"]["evidence"][0]["id"])

# R02（不清空，接续状态）
d2 = post({"case_id": "R02", "reset": False})
b, f = d2["baseline"], d2["fixed"]
print("\nR02 修复前:", b["answer"], "| evidence:", [e["id"] for e in b["evidence"]],
      "| cache_hit:", b["cache_hit"], "| support:", b["support_status"])
print("R02 修复后:", f["answer"], "| evidence:", [e["id"] for e in f["evidence"]],
      "| cache_hit:", f["cache_hit"], "| support:", f["support_status"])

# 页面首页可访问
with urllib.request.urlopen("http://127.0.0.1:8766/", timeout=10) as r:
    html = r.read().decode()
print("\n页面加载:", len(html), "bytes; 含'修复前后对照':", "修复前后对照" in html)

# 判定
ok = ("12" in f["answer"] and [e["id"] for e in f["evidence"]] == ["b02"]
      and "30" in b["answer"] and b["cache_hit"])
print("\nE2E 结论:", "PASS — 修复前复现旧结论，修复后返回当前版本结论" if ok else "FAIL")
