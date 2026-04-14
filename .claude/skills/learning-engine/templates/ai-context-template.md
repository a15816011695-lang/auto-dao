# AI Context（AI 专用上下文 — 非用户文档）

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

| 维度 | 观察 |
|------|------|
| 背景水平 | {background_level} |
| 认知偏好 | {cognitive_preference} |
| 常见错误模式 | {error_patterns} |
| 答题风格 | {answer_style} |
| 认知难度反馈 | {difficulty_feedback} |

## 错误模式分析

<!-- 从错题记录中提炼的高频错误类型，用于遗忘检测和动态支架决策 -->

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
