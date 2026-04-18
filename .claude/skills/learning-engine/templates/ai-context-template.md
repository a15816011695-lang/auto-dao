# AI 专用上下文 (AI Context)

<!-- 本文件由学习引擎自动维护，供 AI 快速恢复会话上下文。用户无需编辑。 -->

## 会话元数据

| 字段 | 值 |
|------|-----|
| 主题 ID | {topic_id} |
| 资料来源 | `{source_path}` |
| 资料格式 | {format}（原始）→ Markdown（转换后） |
| 转换后路径 | `{converted_path}` |
| 创建时间 | {created_at} |
| 最后活跃 | {last_active} |
| 课时进度 | {completed}/{total} |

## 用户画像快照

> **权威源**：`session_state.json` → `learner_model`
> 以下字段的详细数据以 learner_model 为准，本节仅为人可读摘要。

| 维度 | 值 | 来源 |
|------|-----|------|
| 目标 Bloom 层级 | L{bloom_target} | session_state.learner_model.bloom_target |
| 整体自信度偏差 | {overall_confidence_bias} | learner_model.overall_confidence_bias |
| 偏好节奏 | {preferred_pace} | learner_model.preferred_pace |
| 已测概念数 | {concept_count} | learner_model.concept_mastery 长度 |
| 整体掌握率 | {overall_mastery_rate}% | learner_model 聚合计算 |

## 错误模式分析

> **权威源**：`session_state.json` → `learner_model.concept_mastery[<concept_tag>].misconception_tags`
> 以下数据从 learner_model 派生，用于遗忘检测和动态支架决策。

<!-- 从 learner_model.concept_mastery[concept_tag].misconception_tags 聚合提炼高频错误类型 -->

| 错误类型 | 频次 | 典型表现 | 建议策略 |
|---------|------|---------|---------|
| {type} | {count} | {description} | {strategy} |

## 教学决策日志

<!-- 记录关键教学决策及其依据，帮助后续会话保持一致性 -->

| 课时 | 决策 | 依据 |
|------|------|------|
| Lesson {n} | {decision} | {rationale} |

## 断点恢复信息

> ⚠️ 以下字段的权威值来自 `session_state.json`。本节仅为人可读摘要，若与 JSON 冲突以 JSON 为准。

| 字段 | 值 |
|------|-----|
| 最后完成课时 | Lesson {n} |
| 当前课时状态 | {status: 未生成/已生成待答/已批改} |
| 待处理事项 | {pending_items} |
| 未纠正错题数 | {uncorrected_count} |
| 距上次学习天数 | {days_since_last}（运行时计算） |
