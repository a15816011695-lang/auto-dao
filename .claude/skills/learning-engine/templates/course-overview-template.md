# 课程概览 (Course Overview)

**主题**: {topic_name}
**学习周期**: {start_date} ~ {end_date}
**总课时数**: {total_lessons}
**创建时间**: {created_at}

---

## 学习目标

本课程学习结束后，你将能够：

1. {goal_1}
2. {goal_2}
3. {goal_3}

---

## 知识地图

```
{topic_name}
│
├── 📦 模块 1: {module_1_name}
│   ├── L{lesson_1}: {lesson_1_title} [{bloom_level}]
│   ├── L{lesson_2}: {lesson_2_title} [{bloom_level}]
│   └── L{lesson_3}: {lesson_3_title} [{bloom_level}]
│
├── 📦 模块 2: {module_2_name}
│   ├── L{lesson_4}: {lesson_4_title} [{bloom_level}]
│   └── L{lesson_5}: {lesson_5_title} [{bloom_level}]
│
└── 📦 模块 3: {module_3_name}
    └── L{lesson_6}: {lesson_6_title} [{bloom_level}]
```

---

## 课程依赖关系

```mermaid
graph LR
    L{lesson_1}["L{lesson_1}\n{lesson_1_title}"] --> L{lesson_2}["L{lesson_2}\n{lesson_2_title}"]
    L{lesson_2} --> L{lesson_3}["L{lesson_3}\n{lesson_3_title}"]
    L{lesson_3} --> L{lesson_4}["L{lesson_4}\n{lesson_4_title}"]
    L{lesson_4} --> L{lesson_5}["L{lesson_5}\n{lesson_5_title}"]
    L{lesson_5} --> L{lesson_6}["L{lesson_6}\n{lesson_6_title}"]
```

---

## 各课速览

### Lesson {lesson_1}: {lesson_1_title}

| 属性 | 值 |
|------|-----|
| **目标认知层级** | {bloom_level_1} |
| **知识类型** | {knowledge_type_1} |
| **核心概念** | {concept_tags_1} |
| **前置要求** | {prerequisites_1} |

**本课目标**：{objective_1_summary}

---

### Lesson {lesson_2}: {lesson_2_title}

| 属性 | 值 |
|------|-----|
| **目标认知层级** | {bloom_level_2} |
| **知识类型** | {knowledge_type_2} |
| **核心概念** | {concept_tags_2} |
| **前置要求** | Lesson {lesson_1} |

**本课目标**：{objective_2_summary}

---

### Lesson {lesson_3}: {lesson_3_title}

| 属性 | 值 |
|------|-----|
| **目标认知层级** | {bloom_level_3} |
| **知识类型** | {knowledge_type_3} |
| **核心概念** | {concept_tags_3} |
| **前置要求** | Lesson {lesson_1}, {lesson_2} |

**本课目标**：{objective_3_summary}

---

## 知识点脉络

### 概念演进路径

| 阶段 | 核心概念 | 演进关系 |
|------|---------|---------|
| 入门 | {concept_1} | 基础定义，建立认知 |
| 进阶 | {concept_2} | 在 {concept_1} 基础上深化 |
| 应用 | {concept_3} | 综合运用 {concept_1} + {concept_2} |
| 拓展 | {concept_4} | 边界案例与实际场景 |

### 关键概念图谱

```
        ┌─────────────────────────────────────┐
        │           {concept_central}           │
        │           (核心概念)                  │
        └──────────┬──────────────┬──────────────┘
                   │              │
        ┌──────────┴──┐    ┌─────┴──────────┐
        │ {concept_a} │    │  {concept_b}   │
        │ (前置概念)  │    │  (相关概念)     │
        └─────────────┘    └────────────────┘
```

---

## 学习建议

### 适合的学习顺序

1. **按依赖顺序**：从 Lesson 1 开始，依次学习
2. **按模块学习**：每个模块内完成后再进入下一个
3. **按需跳转**：有基础可直接从中间开始

### 时间规划

| 阶段 | 建议时长 | 覆盖范围 |
|------|---------|---------|
| 快速学习 | ~{quick_duration} 小时 | 核心概念 + 练习 |
| 标准学习 | ~{standard_duration} 小时 | 完整讲解 + 练习 + 反思 |
| 深度学习 | ~{deep_duration} 小时 | 完整讲解 + 挑战题 + 拓展阅读 |

---

## 关联资源

### 学习资料来源

| 序号 | 资料名称 | 路径 | 覆盖范围 |
|------|---------|------|---------|
| 1 | {source_1_name} | `{source_1_path}` | Lesson {coverage_1} |
| 2 | {source_2_name} | `{source_2_path}` | Lesson {coverage_2} |

### 配套图表

> 以下图表优先引用资料原图，理解性图示才生成 DrawIO。

| 图表类型 | 来源 | 说明 |
|---------|------|------|
| 架构图 | `{source_image_path_1}` | 来自资料原图 |
| 时序图 | `diagrams/{diagram_name}.drawio` | 需生成理解性图示 |

---

## 进度追踪

> 学习过程中，本文件的进度部分会自动更新。

### 当前进度

```
{completed_lessons}/{total_lessons} Lessons ({progress_percentage}%)

{'█' * int(progress_percentage/10)}{'░' * (10-int(progress_percentage/10))} {progress_percentage}%
```

### 已完成课时

| Lesson | 完成日期 | 掌握度 | 备注 |
|--------|---------|--------|------|
| {completed_rows} |
| — | — | — | 暂无完成记录 |

---

*最后更新: {last_updated_at}*
