# b_diagnosis.md — 故障诊断（修复前）

> 数据源：`results/b/baseline.json`（修复前原样机）、`tools/b_experiment.py` 输出、
> 预测文件 `results/b/b_predictions.md`（写于实验之前）
> 主问题：**R02 — 换了资料版本却显示旧结论**

## 1. 代码确认的事实（读 challenge.py 即可确认，无需实验）

| # | 事实 | 代码位置 |
|---|---|---|
| F1 | 缓存键 = `request['query'].strip().lower()`，**不含 doc_ids / snapshot / k** | `evaluate()` 中 `key = ...` 行 |
| F2 | 全库排序截断 `ranked[:request['k']]` **先于** scope 过滤（doc_ids/snapshot） | `selected = ranked[:k] ...` → `evidence = [b for b in selected ...]` |
| F3 | `support_status` 仅由引用ID是否⊆evidence 决定（`valid → supported`），**无任何语义验证** | `result = {... 'support_status': 'supported' if valid else 'not_checked' ...}` |
| F4 | 无任何 `invalid_scope` 状态；doc_ids 不存在时照样走检索并返回 `status='ok'` | 全函数无该分支 |
| F5 | 引用检查只有单一 `valid/invalid`，未按 spec#3 区分"缺失"与"越界" | 同 F3 行 |

## 2. 待检查的解释（与已有证据相容的候选原因）

- **H1（缓存污染）**：R02 复用 R01 的 v1 结果 → 返回旧版本结论。
- **H2（排序先于范围过滤）**：scope 外条目挤占 k 名额 → scope 内证据丢失。
- H1/H2 均与"R02 显示 30秒"相容（实验前无法区分）。

## 3. 实验建立的因果关系（预测先行，见 b_predictions.md）

| 实验 | 结果 | 判定 |
|---|---|---|
| E1 全新实例只跑 R02 | **12秒 / evidence=[b02] / cache_hit=False** | 符合 H1 预测 |
| E1b 复刻 R01→R02 顺序 | **30秒 / evidence=[b01] / cache_hit=True**（症状精确复现） | 与 baseline 一致 |
| E2 全新实例跑 R03 | **evidence=[]**（缓存不参与仍失败） | H2 独立成立 |
| C1 缓存键源码检查 | 键只含 query（F1） | 代码事实 |
| C2 draft 侧排除 | R02 的 draft 原文为 12秒/b02（正确），错误输出却为 30秒 | 错误产生于引擎，非 draft |

**因果结论**：
1. **R02 归因 H1（缓存污染）**：新鲜实例正确 + 顺序复现 + 键缺失源码事实，
   三点构成完整因果链（必要条件被 E1 排除，充分性由 E1b 复现）。
   H2 对 R02 未触发（k=2 足够，b01/b02 都进 selected，scope 过滤后留下 b02）。
2. **H2 独立存在**：R03 在完全不涉及缓存的条件下仍丢失 scope 内证据（k=1 被
   scope 外的 b01 占走），与 R02 分离，属第二个故障。
3. **反向因果检查 C1**：R02 的耗时短（0.016ms vs 0.081ms）是"走了缓存"的结果，
   不能反推"处理更快"或"功能正常"——耗时差异不作正确性证据。
4. **评价错误检查 C2**：R04 的 supported 并非"全部 not_checked"式保守造成
   （R01/R05/R06 均 supported），而是 F3"ID有效即supported"直接导致。

## 4. 四症状的归因汇总（主问题 + 风险登记）

| 症状 | 根因（代码） | 归因实验 | 处理 |
|---|---|---|---|
| **R02 旧结论**（主） | F1 缓存键缺维度 | E1/E1b | **最小修复对象** |
| R03 证据丢失 | F2 排序先于过滤 | E2 | 修复（与主修复同属检索正确性） |
| R04 假 supported | F3 无语义验证 | C2 + 原文对照 | 按 spec#4 处理（见修复说明） |
| R07 无 invalid_scope | F4 缺状态分支 | 代码事实 | 修复（spec#1 明确要求） |

## 5. 未解决 / 未验证边界（如实登记）

- R02 单次失败是确定性行为（E1b 一次复现），未做多次重复统计（离线确定性代码，预期确定）。
- 语义验证采用轻量规则（数值比对 + 限定词检测），**不是通用语义判断**；
  对未见过的表述形态可能失效——见修复后自构造边界用例。
- 样机无真实网络/并发，多 worker 场景行为**未测**（spec#6），不作结论。
