# 学习摘要 (Learning Summary)

<!-- 本文件为派生视图，核心进度以 session_state.json 为准。笔记、错题记录等补充信息可直接在此追加。 -->

**主题**: {topic_name}
**开始时间**: {start_timestamp}
**最后更新**: {last_update_timestamp}
**完成课时**: {completed_lessons} / {total_lessons}

---

## 核心问答（持续积累）

> 快速复习专用。问题 → 回忆 → 对照答案检验。

| # | 知识点 | 课时 | 问题 | 答案 | 状态 |
|---|--------|------|------|------|------|
| 1 | {concept_1} | L{lesson_n} | {question_1} | {answer_1} | ✅ |
| 2 | {concept_2} | L{lesson_n} | {question_2} | {answer_2} | 🔄 |
| 3 | {concept_3} | L{lesson_n} | {question_3} | {answer_3} | ⏳ |

---

## 错题记录

> 每次答案检查中"部分正确"或"错误"的习题记录于此。纠正后更新状态。

| 课时 | 题号 | 错误摘要 | 类型 | 首次 | 最近 | 状态 |
|------|------|---------|------|------|------|------|
| L{n} | 习题 {m} | {error_summary} | {概念/程序/推理} | {date_1} | {date_2} | ❌ 未纠正 |

**错误类型说明**：
- 概念 = 对定义或含义的理解偏差
- 程序 = 操作步骤或计算过程出错
- 推理 = 逻辑推导链断裂或跳跃

---

## 核心结论（每课追加）

### L{n} {lesson_title}

- **结论 1**：{conclusion_1}
- **结论 2**：{conclusion_2}
- **关键公式**：{formula_if_any}

> 📖 来源：Lesson {n} → [{lesson_file_path}](lessons/lesson_{n}.md)

---

## 已掌握知识点

> **数据来源**：`session_state.json` → `learner_model.concept_mastery`

| Concept Tag | Lesson | Bloom | 自信度偏差 | 测试次数 |
|-------------|--------|-------|-----------|---------|
| {topic}-{concept-a} | L{n} | L{bloom} | {bias} | {count} |

---

## 待攻克难点

| 知识点 | 状态 | 建议 |
|--------|------|------|
| {difficulty_1} | ⚠️ 待巩固 | {suggestion_1} |
| {difficulty_2} | ⏳ 待学习 | {suggestion_2} |

---

## 学习进度

```
{completed_lessons}/{total_lessons} Lessons ({progress_percentage}%)

{'█' * int(progress_percentage/10)}{'░' * (10-int(progress_percentage/10))} {progress_percentage}%
```

---

## 下次学习计划

1. {next_plan_1}
2. {next_plan_2}

---

*本文件由学习引擎自动维护。核心状态数据以 `session_state.json` 为准。*
