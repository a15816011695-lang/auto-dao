# 2026-04-18 · 学习教程生成链路优化总结

> 上下文：用户要求"深度思考，优化学习教程生成链路的全部环节"。本次优化聚焦 **P0/P1 级一致性 Bug** 以及 **AI 可调用入口脚本**，不扩展新的功能面。

## TL;DR

| 分类 | 改动 | 影响 |
|------|------|------|
| P0 · Schema | `session-state.schema.json` 版本 `2.0` → `2.2`；补 `topic_name` / `_file_paths` properties | 模板初始化的 session_state 现在能通过严格 jsonschema 校验 |
| P0 · 命名 | 派生视图文件统一纯名（`summary.md/roadmap_status.md/_ai_context.md`），去 `Sys.NN_` 前缀 | SKILL.md、CI、examples、脚本全部对齐，不再有"两套命名" |
| P0 · 路由 | `diagnostic_grader.py` 实现完整四档路由（Skip/Compact/**Full**/Remedial，基于 `confidence_bias`） | Step 3.5.5 规格完整落地；新增 `classify_confidence_bias` + `infer_dominant_bias` 工具函数 |
| P0 · SKILL 流程 | Step 4.5 序号去重（6 出现两次 → 重编号 1-11）；Step 1.4/1.5 "subagent 轮询" 改为同步 CLI 调用 | AI 按序执行不错位；不再出现无法落地的 `poll_interval=10s` 伪流程 |
| P1 · 集成 | Step 2 新增"大测驗知识图谱检测"子步；Step 3 新会话初始化补 `course_overview.md` | comprehensive-assessment 首次与 learning-engine 真正联通 |
| P1 · 诊断 | `prereq-diagnostic-*.md` 加 `concept_tag` 字段，绑回 `learner_model.concept_mastery` | 批改结果可以直接更新学习者模型 |
| P1 · Metrics | `metrics-template.json` 1.0→1.1，定义 13 类事件枚举 + schema hint | AI 写事件时有明确的枚举集合可选 |
| P1 · CF Mode | SKILL 里"仅本次开启/关闭"明确不修改 `counterfactual_mode` 字段，改写入 `metrics.counterfactual_toggled` | 不再与 schema enum 冲突 |
| P2 · 脚本 | 新增 `scripts/session/init_session.py`：一条命令创建完整会话骨架 + 自动通过 `validate_state.py` | AI/用户都可用；测试覆盖 11 项 |
| P2 · 文档 | 本总结 + README 故障排查段 | maintainer 可追溯 |

测试基线：`pytest` 从 **191 passed** 扩至 **215 passed**（新增 24 项）。

---

## 重点设计决策

### 1. 为什么派生视图用纯名而不是 `Sys.NN_` 前缀

前缀方案的本意是：文件按字母排序即可呈现"权威源 → 派生视图"的层级。但代价是：

- SKILL.md 所有散文 prose 都写纯名（`summary.md`）
- `scripts/session/validate_state.py`、`scripts/ci/check_examples.py`、`tests/conftest.py` 也都用纯名
- `examples/learning-history/golden-example/` 用纯名
- **只有 template 文件头部与 `_file_paths` 用前缀**

维持两套命名需要改代码、CI、示例、tests、SKILL.md 全部——工作量大且无收益。选"全部纯名"更便宜、更一致。`_file_paths` 字段保留作为 **未来自定义能力的扩展点**（schema 允许 additionalProperties）。

### 2. 四档路由为什么是这种升级方式

SKILL.md Step 3.5.5 规定：

| 掌握度 | 主导 bias | 路由 |
|--------|-----------|------|
| ≥ 80% | 任意 | Skip |
| 60-79% | calibrated | Compact |
| 60-79% | over/underconfident | **Full** |
| < 60% | 任意 | Remedial |

实现选择：`get_route(pct, dominant_bias=None)` 保留旧单参签名以兼容。只有 **Compact 区间且 bias ∈ {overconfident, underconfident}** 时升级为 Full。这样：

- `ROUTE_TABLE[70]` 仍返回 `"compact"`（旧测试不破）
- 新参数传入 `"overconfident"` 时返回 `"full"`
- 边界 (80/59) 上 bias 不影响结果 — 符合 Spec

`infer_dominant_bias` 的"优先级打破平手"规则：`overconfident > underconfident > uncertain > calibrated`。理由：过度自信对学习最危险，需要最多脚手架，故在并列时优先触发 Full。

### 3. Subagent 描述为什么要删

learning-engine 运行在 AI 的内联上下文里，没有**真实**可轮询的子代理。SKILL.md 之前的描述：

> 启动 subagent（`general-purpose` 类型），...
> 轮询检查 subagent 状态（poll_interval = 10s，最大等待 300s）

是**伪流程**——AI 无法执行"每 10 秒检查一次"。保留它意味着：
- 新人阅读 SKILL.md 以为必须某种基础设施
- AI 按字面执行时会 confused 或"假装"轮询

改成 **同步 CLI 调用** (`python .claude/skills/everything-to-markdown/scripts/convert_to_markdown.py`) 后，行为可验证、可复制、可在 CI 里测试。

### 4. `init_session.py` 的定位

此脚本不做业务决策——只搭骨架。运行后：

1. 目录和所有派生视图存在
2. `session_state.json` 的 schema-required 字段已填（不经过它会违反 schema）
3. `validate_state.py` 立即通过（端到端测试已验证）
4. 业务占位符（`{topic_name}` / `{concept_1}` …）保持原样等待 AI 填写

SKILL.md Step 3 提示 AI 可以用它作为初始化入口，但允许 AI 手动执行等价步骤。

---

## 未纳入本次的后续建议（留给 maintainer）

| 优先级 | 项目 | 说明 |
|--------|------|------|
| P2 | `everything-to-markdown` 批量模式 | 当前一次一个文件；多 PDF 教材要手动循环 |
| P2 | `report.md` 认知层级分布聚合 | Template 有字段但 SKILL.md 未给出"从 lesson 元信息聚合"的步骤 |
| P2 | `report.md` concept_tag 进度视图 | 可从 `learner_model.concept_mastery` 派生 |
| P3 | `tmp/converted/` 索引注册 | 多次转换会累积文件 |
| P3 | `auto-dao init` 向导 | 交互式首次配置 `.env`、`background.md`、`glossary.md` |
| P3 | mypy 目前 `--ignore-missing-imports`；考虑加 `scripts/session/*.py` 的严格化 | 捕捉更多签名 Bug |

---

## 兼容性说明

- **旧会话目录**（`schema_version == "2.0"`）在 `validate_state.py` 下会报 `schema_version` 不匹配——属**有意为之**，提示用户 migrate。`golden-example` 已升级到 2.2 作为示范。
- `ROUTE_TABLE` 单参查询保持原返回值（三档），只有显式传入 `dominant_bias` 才进入四档逻辑。
- `grade_diagnostic_file` 额外增加了 `full` / `dominant_bias` 两个返回键；旧调用点只读取 `mastery_pct / route / scores` 的不受影响。
- `metrics-template.json` schema_version 从 `"1.0"` → `"1.1"`，新增字段以 `_` 前缀，向后兼容。

---

*生成时间：2026-04-18 · 所有改动由 Cascade 执行，全量 `pytest` 通过。*
