"""fixed_engine.py — 诊断后的最小修复实现（保留 Engine 接口）。

对应 results/b/b_diagnosis.md 的四项根因：
  F1 缓存键缺维度（主问题 R02）→ 键纳入 query+doc_ids+snapshot+k
  F2 排序先于范围过滤（R03）  → 先按 scope 过滤，再排序取 k，再保留正分
  F3 ID有效即supported（R04）  → 轻量语义验证，未验证时 not_checked/insufficient
  F4 缺 invalid_scope（R07）   → 未知 doc_id 返回 status=invalid_scope
  F5 引用状态未分型（spec#3）  → locator_status 区分 missing / out_of_scope / valid

spec#5 允许"保留缓存但须验证等价输入"：本实现缓存键覆盖全部请求维度；
corpus 在离线重放中固定，若 corpus 可变需一并入键（见 README 边界说明）。
"""
import copy
import re
import time
import uuid

# 证据文本中的"限定性"标记：原文承认未测量/未测试
LIMIT_MARKERS = ("没有测量", "未测量", "未测试", "没有对", "与实验A无关")
# 答案中的"绝对断言"词：与限定标记同现时不能判 supported
ABSOLUTE_WORDS = ("保证", "一定", "立即", "完全", "就会", "必然")


def _split_scope(corpus, request):
    """按 spec#1 划定范围；未知 doc_id → (None, unknown)。"""
    known_docs = {b["doc_id"] for b in corpus}
    unknown = [d for d in request["doc_ids"] if d not in known_docs]
    if unknown:
        return None, unknown
    scoped = [b for b in corpus
              if b["doc_id"] in request["doc_ids"] and b["snapshot"] == request["snapshot"]]
    return scoped, []


def _rank_select(scoped, query, k):
    """spec#2：scope 内排序取 k，分数相同按 id 字典序，只保留正分。"""
    terms = set(query.strip().lower().split())
    ranked = sorted(scoped, key=lambda b: (-len(terms & set(b["tags"])), b["id"]))
    return [b for b in ranked[:k] if terms & set(b["tags"])]


def _check_citations(citations, evidence, corpus):
    """spec#3：valid / missing / out_of_scope 三态。"""
    if not citations:
        return "missing"
    all_ids = {b["id"] for b in corpus}
    ev_ids = {b["id"] for b in evidence}
    if any(c not in all_ids for c in citations):
        return "missing"
    if not set(citations).issubset(ev_ids):
        return "out_of_scope"
    return "valid"


def _check_support(answer, evidence, locator):
    """spec#4：独立于ID的轻量语义验证；不足时如实 not_checked/insufficient。

    规则（针对本样机披露的轻量启发式，非通用语义判断）：
      R1 引用无效 → not_checked
      R2 答案含数值 → 数值须出现在证据文本中，否则 insufficient
      R3 绝对断言词 与 证据中的未测量/未测试限定标记 同现 → insufficient
      R4 其余 → supported（附 basis）
    """
    if locator != "valid":
        return "not_checked", "引用无效，无法验证语义"
    joined = "".join(e["text"] for e in evidence)
    nums = re.findall(r"\d+", answer)
    if nums:
        if all(any(n in e["text"] for e in evidence) for n in nums):
            if any(m in joined for m in LIMIT_MARKERS) and \
               any(w in answer for w in ABSOLUTE_WORDS):
                return "insufficient", "证据含未测量限定，答案为绝对断言"
            return "supported", "答案数值均可在证据文本中定位"
        return "insufficient", "答案数值无法在证据文本中定位"
    if any(m in joined for m in LIMIT_MARKERS) and any(w in answer for w in ABSOLUTE_WORDS):
        return "insufficient", "证据含未测量限定，答案为绝对断言"
    if any(m in joined for m in LIMIT_MARKERS) and any(w in answer for w in LIMIT_MARKERS):
        return "supported", "答案与证据同为限定性陈述且语义一致"
    return "supported", "答案关键内容与证据文本一致（轻量核对）"


class Engine:
    def __init__(self):
        self.cache = {}

    def _cache_key(self, request):
        return (request["query"].strip().lower(),
                tuple(request["doc_ids"]), request["snapshot"], request["k"])

    def evaluate(self, request, corpus, draft):
        started = time.perf_counter()

        scoped, unknown = _split_scope(corpus, request)
        if unknown:
            # F4/spec#1：未知组合返回 invalid_scope，不回退、不检索
            result = {"status": "invalid_scope", "answer": draft["answer"],
                      "citations": draft["citations"], "evidence": [],
                      "locator_status": _check_citations(draft["citations"], [], corpus),
                      "support_status": "not_checked",
                      "support_basis": "范围无效（未知文档：%s），未做语义判断" % ",".join(unknown),
                      "judgment_source": "rule",
                      "invalid_docs": unknown}
        else:
            key = self._cache_key(request)
            hit = key in self.cache
            if hit:
                result = copy.deepcopy(self.cache[key])
            else:
                evidence = _rank_select(scoped, request["query"], request["k"])
                citations = draft["citations"]
                locator = _check_citations(citations, evidence, corpus)
                support, basis = _check_support(draft["answer"], evidence, locator)
                result = {"status": "ok", "answer": draft["answer"],
                          "citations": list(citations),
                          "evidence": copy.deepcopy(evidence),
                          "locator_status": locator, "support_status": support,
                          "support_basis": basis, "judgment_source": "rule"}
                self.cache[key] = copy.deepcopy(result)

        result.update(request_id=str(uuid.uuid4()),
                      request=copy.deepcopy(request),
                      cache_hit=bool(locals().get("hit", False)),
                      elapsed_ms=(time.perf_counter() - started) * 1000,
                      run_kind="offline_replay")
        return result
