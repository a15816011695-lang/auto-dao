# 术语表 (Glossary)

> `concept_tag` ↔ 中文关键词 ↔ 术语定义 三者的权威映射源。
> **1:1:1 原则**：每个 `concept_tag` 唯一对应一个中文关键词与一条术语定义，严格对齐。
> 设计依据：`docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §四、§附录 B。

---

## 列定义

| 列 | 含义 | 格式示例 |
|---|------|---------|
| **concept_tag** | 机器可读 slug；lesson 元信息 / `learner_model.concept_mastery` / prereq-map 均以它为键 | `stm32-eeprom-page-wrap` |
| **中文关键词** | 学习者可见的自然语言短词；思考模块中以反引号包裹使用 | `卷绕机制` |
| **英文** | 英文标准名或学科通用英文表达 | `page wrap` |
| **定义** | 一句话术语解释（避免长段落，详细讲解放 lesson 正文） | `EEPROM 超出页大小时数据覆盖页首` |
| **首次出现** | 主题名 · Lesson 编号；跨主题重复以最早一次为准 | `STM32 · Lesson 3` |

> `concept_tag` 命名格式为 `{topic}-{concept-name}`，全小写、连字符分隔；规范见 `.claude/skills/learning-engine/SKILL.md §4.1 第 6 步`。
> 历史遗留条目若暂无 `concept_tag`，允许填 `—`（与 §九 Q7 决策一致：不强制回填旧 session）。

---

## 数学 (Mathematics)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| — | 函数 | Function | 描述输入与输出之间的对应关系 | 一元函数微分学 |
| — | 导数 | Derivative | 描述函数在某点的瞬时变化率 | 一元函数微分学 |

---

## 心理学 (Psychology)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 哲学 (Philosophy)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 计算机科学 / 嵌入式 (Computer Science / Embedded)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| stm32-eeprom-page-wrap | 卷绕机制 | page wrap | EEPROM 写入跨过页边界时指针回绕至页首、覆盖原有数据 | STM32 · Lesson 3 |

> 本条目为设计示范（参考 `docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §附录 B）。
> 实际 STM32 全栈课程的术语条目将在对应 session 生成 lesson 时，由 AI 按元信息中的 `concept_tags` 字段同步补录（Q5 决策：模板与 glossary 同步改造）。

---

## 使用说明

1. **按学科/主题分类维护**：新增学科时追加二级标题节，表头固定为 5 列；不要改列顺序。
2. **1:1:1 对齐**：
   - 每个 `concept_tag` 只对应一条中文关键词与一条定义
   - 跨主题同义术语应合并为同一条目，"首次出现"列填最早一次
3. **`concept_tag` 命名规范**：
   - 格式 `{topic}-{concept-name}`，全小写、连字符分隔
   - 示例：`stm32-gpio-mode`、`c-pointer-arithmetic`、`transformer-self-attention`、`adlerian-separation-of-tasks`
   - `topic` 建议取自 `roadmap_status.md` 的主题 slug 或主流学科英文简称
4. **"首次出现"格式**：`{主题名} · Lesson {N}`；若主题名较长可用缩写（如 `STM32-HAL · L3`）。
5. **新增术语的流程**（对应阶段 B 开始后的日常操作）：
   1. AI 在 `lesson-template.md` 元信息写入 `concept_tags: [...]`
   2. 同步将每个 tag 加入本表（或更新"首次出现"）
   3. 思考模块（L1）预生成关键词索引时，从本表反查中文关键词
6. **迁移策略**（与设计文档 §九 Q5 / Q7 决策一致）：
   - 旧 session 保持现状，不强制回填历史 lesson 的 concept_tag
   - 历史条目允许 `concept_tag` 列填 `—`，新增条目必须写全
7. **校验**（人工）：每季度 review 一次，查找：
   - 同一 `concept_tag` 在多行出现（违反 1:1:1）
   - `concept_tag` 命名不符格式（大写字母、下划线、空格等）
   - "首次出现"指向已不存在的 session