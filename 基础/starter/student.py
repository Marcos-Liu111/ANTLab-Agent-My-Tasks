"""student.py — 文档阅读与信息核验的证据组织实现。

设计说明（prompt 设计依据，见 decisions.md）：
1. 四元组精确匹配：题目要求按 项目/版本/月份/批次/指标口径 精确核对，
   prompt 中显式列出这些字段，要求模型逐字段比对而非关键词相似度。
2. 跨段计算开放：基础题存在分子分母分处两段的情况（如 D01 的 68/85），
   因此允许多段组合，但引用必须逐一列出被使用的段落ID。
3. 证据不足优先：字段对不上时返回"证据不足"，禁止用相近批次/月份的数据顶替，
   这是防止编造的核心约束。
4. 输出契约固定：严格 JSON {"answer","citations"}，便于 runner 解析与复算。
"""

SYSTEM_PROMPT = """你是一个文档核验助手。你的任务是从给定的资料段落中找到能精确回答问题的证据。

## 匹配规则（必须逐字段核对，不能只看关键词相似）

问题中通常包含这些定位字段，必须在段落中全部精确匹配后才能作为证据：
- 项目名称（如：澄石项目 vs 岫光项目）
- 版本号（如：R3 vs R4）
- 月份/时间窗口（如：2026-03 vs 2026-02）
- 批次类型与代号（如：正式回归批次CS41 vs 迁移批次XQ50 vs 探索组 vs 压力组）
- 指标口径（如：支持率 vs 核验率；分母是有效问题数还是返回成功数）

任何一个字段不匹配，该段落就不能作为答案依据（即使数字很接近）。

## 回答规则

1. 只依据给定段落作答，禁止使用外部知识或凭空推断。
2. 可以跨段落组合证据（例如分子在一段、分母在另一段），此时每一段都要列入引用。
3. 需要计算时，先在心里明确分子分母来自哪个段落，再给出结果。
4. 如果所有段落中都找不到字段完全匹配的记录，回答"证据不足"，
   并把最接近但不满足条件的段落ID列入 citations（表示你检查过这些来源）。
5. 答案要简短：按题目要求的格式输出（百分数、数值、简短词组等）。
6. 引用的每个段落ID必须真实出现在本次输入中，禁止编造ID。

## 输出格式

只输出一个JSON对象，不要输出任何其他文字：

{"answer": "简短答案", "citations": ["段落ID1", "段落ID2"]}

注意：
- answer 是字符串
- citations 是字符串数组，即使只有一个证据也要用数组
- 证据不足时 answer 为 "证据不足"
"""


def prepare_messages(question, passages):
    """返回 [{"role":"system|user", "content":"..."}, ...]。

    passages仅含id/source/text，不包含答案或条件标记。
    必须请求JSON对象: {"answer": "简短答案", "citations": ["P..."]}。
    """
    lines = []
    for i, p in enumerate(passages, 1):
        # 保留原始 id/source/text，不做任何重映射
        lines.append(f"[段落{i}] ID: {p['id']} | 来源: {p['source']}\n{p['text']}")

    user_content = (
        f"## 问题\n{question}\n\n"
        f"## 资料段落（共{len(passages)}段）\n\n"
        + "\n\n".join(lines)
        + "\n\n请根据以上段落回答问题，严格输出JSON。"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def improve(question, passages):
    """返回重新组织/选择的原段落列表，不能修改id/source/text或使用答案标签。

    当前为默认恒等映射（基线联通用），改进方案在冻结后实现（见 D4）。
    """
    return passages
