# ANTLab Agent Tasks — 提交作品

> 本仓库为基础题与进阶 **B 题**（源码审查、故障归因与修复）的整合提交。
> 下方「提交说明」为本人的作品入口；再往下的「题包原始说明」为考核方提供的 README，原样保留。

---

## 提交说明

### 环境

- Python 3.10+（本机 3.14.5），仅标准库（无第三方依赖）
- 模型服务：AIXForge 网关（OpenAI 兼容），模型 `glm-5.3`
- 环境变量：`ASSESSMENT_API_KEY`（**不入库**；`基础/config.local.json` 亦不入库）
- 无密钥配置副本：`configs/run_config.json`

### 启动

```bash
cd 基础
# 1) 本地配置（含 endpoint，不入库）
copy config.example.json config.local.json   # 填入自己的 endpoint/model

# 2) 输入校验（不产生费用）
python starter/runner.py --case D01 --condition E --dry-run --config config.local.json

# 3) 真实调用（会产生模型费用，需显式 --paid）
python starter/runner.py --case D01 --condition E --paid --config config.local.json

# 4) 页面预览
python starter/server.py --config config.local.json
```

### 复算（评审默认使用已有结果离线回放，不产生费用）

```bash
# 逐题汇总表（→ results/baseline_summary.md, results/baseline_runs.csv）
python tools/summarize_runs.py

# 深度分析：顺序一致性 / K 缺失证据 / 耗时异常 / token 汇总
python tools/analyze_baseline.py

# T08 疑点原文核对
python tools/t08_check.py

# 全局统计（调用数、token、分组）
python tools/report_stats.py

# 改进配对（已跑则跳过，不会重复产生费用）
python tools/run_jobs.py

# 改进方法变体检查（纯离线，零费用）
python tools/variant_check.py

# 生成逐题核对表
python tools/gen_verdict_sheet.py
```

### 进阶 B 题（离线，零 API 费用）

```bash
# 修复前基线
cd 进阶/challenge_b
python run_cases.py --engine challenge:Engine --output ../../results/b/baseline.json

# 修复后
python run_cases.py --engine fixed_engine:Engine --output ../../results/b/fixed_official.json

# 页面（修复前后对照）
python server.py --port 8766     # 打开 http://127.0.0.1:8766
```

**关键脚本**（均离线可复算）：
`tools/b_experiment.py`（预测先行的区分性干预）、`tools/b_compare.py`（修复前后逐字段对照）、
`tools/b_variants.py`（回归 + 2 变体 + 自构造边界）、`tools/b_e2e.py`（页面端到端）、
`tools/b_diff.py`（差异定位）。

### 完成 / 未完成

| 项 | 状态 |
|---|---|
| 基础：40 次主请求（32 基线 + 8 改进配对） | ✅ 完成，首次尝试 40/40 成功 |
| 基础：逐题核对（8 题 × 4 条件） | ✅ 完成，24 条全文条件 23 正确 / 1 错误 |
| 基础：一次诊断（T08/R0 顺序异常） | ✅ 完成（H1 支持 / H2 否定，离线） |
| 基础：改进 + 变体检查 | ✅ 完成（23/24 → 24/24，变体三预测全过） |
| 基础：三项决定记录 | ✅ 完成（`decisions.md`） |
| 进阶 B：故障复现、预测、归因、最小修复 | ✅ 完成（4 症状修复，3 案回归零变化） |
| 进阶 B：回归 / 2 变体 / 自构造边界 | ✅ 完成（全 PASS，边界如实登记） |
| 进阶 B：页面展示（修复前后 + 已核验/未核验） | ✅ 完成 |
| 整合报告 | ✅ `report.md` |
| AI 声明 | ✅ `declaration.md` |
| **未完成/未验证** | 见 `declaration.md` §4：B 题语义核验为轻量规则（泛化未验证）；T08/R0 失败确定性未重复统计；多用户/多worker 行为未测；Semantic Reader 未亲测；改进在未公开新题上的泛化未验证 |

### 证据索引（E1–E7）

见 `report.md` 文末表格；各项均可定位到具体文件、run ID 与复算命令。

### 目录（本人新增部分）

```text
report.md                     整合报告（基础 + 进阶B）
declaration.md                AI/他人/复用/未完成声明
decisions.md                  三项关键决定与 AI 影响
reading_notes.md              阅读笔记、三项预期、两项阅读影响
configs/run_config.json       无密钥运行配置
results/                      汇总、核对、配对、B题全部结果
  ├─ baseline_summary.md / baseline_runs.csv / baseline_analysis.md
  ├─ verdict_per_case.md / verdict_summary.md / improved_pairing.md
  └─ b/                       B题：基线/修复/预测/诊断/变体/下一步
tools/                        全部可复算脚本
基础/starter/student.py       基础题实现（含改进版 improve）
进阶/challenge_b/fixed_engine.py  B题最小修复（保留 Engine 接口）
进阶/challenge_b/index.html   B题页面（修复前后对照）
```

---

## 题包原始说明

文档阅读与信息核验方向 Agent 项目的应用层开发者招募考核：先完成基础题，再从进阶 A/B/C 中选择一套完成。

**截止时间：北京时间 2026 年 10 月 16 日 23:59（UTC+8）。**

### 从哪开始

1. 先读 [开始阅读.md](开始阅读.md)（总体规则、时间、提交方式）。
2. 基础题（必做）：[基础/README.md](基础/README.md) 与 基础/01_考核题目.md。
3. 进阶题（三选一）：[进阶/README.md](进阶/README.md)，在 A / B / C 中选一套。

### 目录结构

```text
开始阅读.md              入口：总体规则、截止时间、提交方式
基础/                    基础题：12 题（4 开发题有公开答案 + 8 评测题），
                         R0/R1/R2/K 四种输入组织条件；模型 API 自费，
                         主请求量与运行命令见 基础/README.md
进阶/                    进阶题（A/B/C 三选一）
├─ 01_A_研究机制迁移.md        A：主张→证据→支持状态机制迁移与对照
├─ 02_B_系统失效诊断.md        B：源码审查、故障归因与修复
├─ 03_C_产品假设验证.md        C：围绕自选用户任务的产品假设验证
├─ materials/                 两份 CC Attribution 公开论文（P1/P2）及抽取数据
├─ challenge_b/               B 题文档查证样机（30 行 Engine，含预埋故障）
└─ templates/                 声明与整合报告模板
```

### 规则要点

- 准备时间为一周（包含基础题和进阶题）；模型调用使用自己的 API，费用自理；实验输入、原始响应、失败和前后对照须保留在仓库中。
- AI 可辅助阅读、实现和排错；需记录它对关键决定的影响、本人如何核验，以及实际完成和未完成的内容。
- 提交：把作品推送到自己的 GitHub 仓库，并在收集表登记仓库链接与最终 commit SHA；收集表地址与仓库评审账号见 Q 群公布（详见 进阶/05_提交与报告格式.md 与 进阶/06_收集表填写说明.md）。
- 本包不含评委参考答案、评测标签、内部开发教程或商业书籍全文。
- 文件完整性：`基础/文件校验.json` 与 `进阶/文件校验.json` 提供逐文件 SHA256，可自行校验。
