# 学习路线图状态 (Roadmap Status)

<!-- 本文件为派生视图，进度数据以 session_state.json 为准。 -->

**主题**: {topic_name}
**时间戳**: {timestamp}

---

## 整体进度

```
总进度: {progress_percentage}%
{progress_bar_visualization}
```

---

## 认知坐标

| 维度 | 当前状态 |
|------|---------|
| 当前课时 | Lesson {current_lesson_index} |
| 认知层级 | {current_bloom_level} |
| 掌握程度 | {mastery_level}% |
| 难度感知 | {difficulty_rating}/5 |

---

## 知识点追踪

### 模块 1: {module_1_name}

| 知识点 | 状态 | 测试结果 |
|--------|------|---------|
| {point_1} | ✅ 已掌握 | {test_result_1} |
| {point_2} | 🔄 学习中 | {test_result_2} |
| {point_3} | ⏳ 待学习 | - |

### 模块 2: {module_2_name}

| 知识点 | 状态 | 测试结果 |
|--------|------|---------|
| {point_4} | ⏳ 待学习 | - |
| {point_5} | ⏳ 待学习 | - |

---

## 概念标签与依赖图

> **概念标签（Concept Tags）**：每个 Lesson 的核心知识点标签，用于精确追踪和诊断路由。
> **前置依赖**：哪些 Lesson 必须先完成才能进入本 Lesson。

### 概念标签 → Lesson 映射

| Concept Tag | 所属 Lesson | Bloom | 状态 |
|-------------|------------|-------|------|
| {topic}-{concept-a} | Lesson {n} | L2 | ✅ 已掌握 |
| {topic}-{concept-b} | Lesson {n} | L3 | ✅ 已掌握 |
| {topic}-{concept-c} | Lesson {n+1} | L3 | 🔄 学习中 |
| {topic}-{concept-d} | Lesson {n+2} | L3 | ⏳ 待学习 |

### 前置依赖图（Mermaid）

```mermaid
graph LR
    Lesson_{n}["Lesson {n}\n({topic}-{concept-a})"]
    Lesson_{n+1}["Lesson {n+1}\n({topic}-{concept-b})"]
    Lesson_{n+2}["Lesson {n+2}\n({topic}-{concept-c})"]
    Lesson_{n+3}["Lesson {n+3}\n({topic}-{concept-d})"]

    Lesson_{n} --> Lesson_{n+1}
    Lesson_{n+1} --> Lesson_{n+2}
    Lesson_{n+2} --> Lesson_{n+3}
```

> 依赖图自动从各 Lesson 元信息中的 `prerequisites` 字段派生。手动调整依赖关系时，同步更新各 Lesson 文件的 `前置依赖` 元信息。

---

## 里程碑

- [x] 🎯 里程碑 1: {milestone_1} - {achieved_date}
- [x] 🎯 里程碑 2: {milestone_2} - {achieved_date}
- [ ] 🎯 里程碑 3: {milestone_3} - 预计: {expected_date}
- [ ] 🎯 里程碑 4: {milestone_4} - 预计: {expected_date}
- [ ] 🎁 最终目标: {final_goal}

---

## 学习历史

| 日期 | Lesson | 状态 | 备注 |
|------|--------|------|------|
| {date_1} | Lesson {n} | 完成 | {note_1} |
| {date_2} | Lesson {n+1} | 完成 | {note_2} |
| {date_3} | Lesson {n+2} | 进行中 | {note_3} |

<!-- 补救课与偏题分支示例（按需出现）：
| {date_x} | 🔧 补救课 L{n}_remedial | 完成 | 触发原因：连续 2 课 mastery < 60%，回顾 {知识点} |
| {date_y} | 🔀 分支课 L{n}_branch | 完成 | 用户偏题探索 {topic}，已回归主线 |
-->

---

## 路线调整记录

<!-- 记录何时、为何插入了补救课或偏题分支，用于事后追溯教学决策 -->

| 时间 | 调整类型 | 触发原因 | 影响 |
|------|---------|---------|------|
| {datetime} | 🔧 补救课 | {trigger_reason} | 插入 lesson_{n}_remedial.md |
| {datetime} | 🔀 偏题分支 | {trigger_reason} | 插入 lesson_{n}_branch.md，主线暂停 |

---

## 下一步行动

### 即时任务

- [ ] {immediate_task_1}
- [ ] {immediate_task_2}

### 本周目标

- [ ] {weekly_goal_1}
- [ ] {weekly_goal_2}

---

## 阻塞与风险

| 风险 | 影响 | 解决方案 |
|------|------|---------|
| {risk_1} | {impact_1} | {solution_1} |

---

## 更新日志

### {update_date}

- {update_note_1}
- {update_note_2}
