# Lesson {index}: {lesson_title}

> **文件名约定**（2026-04-18 新标准 · 详见 `SKILL.md §4.2 命名约定`）：
> - 单页课题：`NN_描述.md`（如 `06_四大总线对比.md`）
> - 多子课题拆分：`NN.X_描述.md`（如 `02.0_I2C 协议原理.md`、`02.1_I2C 协议代码.md`）
> - 旧 session 仍兼容 `lesson_N.md` 格式
> - 文件名写入 `session_state.json.lesson_files[index-1]`，作为权威映射

**时间**: {timestamp}
**主题**: {topic_name}
**目标认知层级**: {bloom_level}
**知识类型**: {knowledge_type}
**讲解策略**: {teaching_strategy}

**概念标签**: {concept_tags}                  <!-- 机器 slug，格式：[{topic}-{concept-name}, ...] -->
**概念关键词**: {concept_keywords}          <!-- 学习者可见词（中文或保留英文），与 concept_tags 严格一一对应顺序一致 -->
**前置依赖**: {prerequisites}

---

## 〇、知识导航

> 本课在整体知识体系中的位置。了解"为什么学这个"比"学什么"更重要。

### 知识脉络

```
{topic_name}
│
├── 📦 已学模块：{prev_module_name}
│   └── ✅ L{prev_lesson_index}: {prev_lesson_title}
│
├── 📍 本课（本课）
│   └── 🔄 L{current_index}: {current_title}
│
└── 📦 待学模块：{next_module_name}
    └── ⏳ L{next_lesson_index}: {next_lesson_title}
```

### 本课要回答的核心问题

| 问题 | 答案（学完后再填） |
|------|------------------|
| {core_question_1} | {answer_1} |
| {core_question_2} | {answer_2} |
| {core_question_3} | {answer_3} |

### 知识串联

> 理解本课与其他知识点的关系，建立整体认知。

```
{concept_prev_1} ──→ {concept_current} ──→ {concept_next_1}
    (前置)            (本课)              (后续)
```

**本课定位**：
- 继承自：{prev_concepts}
- 服务于：{next_concepts}
- 对比区分：{confusable_concepts}（容易混淆，注意区分）

---

## 一、学习目标

1. {objective_1}
2. {objective_2}
3. {objective_3}

---

## 二、知识回引

> 路径：`{prev_lesson_1}` → `{prev_lesson_2}` → **`{current_lesson}（本课）`** → `{next_lesson}`

{knowledge_callback_text}

---

## 三、精讲（含 Worked Example）

> **本节目标**：通过完整示范解题过程，建立对"为什么这样解"和"每一步在做什么"的理解。
>
> **代码型知识点附加要求**（知识类型为 `操作性` 或 `程序性` 时强制执行；`概念性` / `原理性` 可省略）：
>
> - 每段 ≥3 行的关键代码块后，必须紧跟一张「代码锚点映射表」（格式见 3.1 示例）
> - Worked Example 之后必须追加「反模式画廊」子节（格式见下方）
> - 渐进训练中的每个空缺必须配「理由项」（格式见 §四）

### 3.1 {section_1_title}

{explanation_with_source_quotes}

> **资料原文**：
> {original_quote_from_material}
>
> [来源：{章节或段落标题}]

<!-- ↓↓↓ 以下为代码锚点格式（操作性/程序性知识点必填；其他类型删除本块） ↓↓↓ -->

**代码示例**：

```{language}
{code_block}
```

**代码锚点映射**（每个魔数 / API / 宏 / 参数回引到原理）：

| 代码符号 | 对应原理（引用前课或本课位置） | 如果不这样会怎样（反事实后果） |
|---------|----------------------------|----------------------------|
| `{symbol_1}` | {principle_ref_1} | {counterfactual_1} |
| `{symbol_2}` | {principle_ref_2} | {counterfactual_2} |
| `{symbol_3}` | {principle_ref_3} | {counterfactual_3} |

<!-- ↑↑↑ 代码锚点格式结束 ↑↑↑ -->

### 3.2 {section_2_title}

{explanation_with_examples}

> ⚠️ 注：{extended_knowledge_point}
> [⚠️ 当前资料未涉及此内容]

### 3.3 {section_3_title}

{additional_explanation}

> 📖 本节参考：{章节1}、{章节2}

### Worked Example — 完整示范

> 以下是本课核心方法的完整解题示范。请仔细阅读每一步推理，体会"为什么这样做"。

**例题**：{worked_example_question}

**完整解答**：

{step_1} → {step_2} → {step_3} → {final_answer}

> - 步骤 1：{why_step_1}
> - 步骤 2：{why_step_2}
> - 步骤 3：{why_step_3}
> - 结论：{why_conclusion}

### 反模式画廊（常见错误代码演示）

> **适用场景**：知识类型为 `操作性` / `程序性` 时强制；其他类型可省略本子节。
>
> **目的**：通过「错误代码 + 失败后果 + 违反的原理」三元组，把"为什么这样写"从正面回答升级为镜像回答——"因为不这样写会 X"。
>
> **要求**：至少 2 个错误片段，每个必须涵盖 ① 错误代码 ② 可观测的失败现象 ③ 违反的原理引用位置。

**❌ 错误 1：{anti_pattern_1_title}**

```{language}
{wrong_code_1}
```

- **后果**：{consequence_1}
- **违反的原理**：{violated_principle_1}（引用位置：{ref_1}）

**❌ 错误 2：{anti_pattern_2_title}**

```{language}
{wrong_code_2}
```

- **后果**：{consequence_2}
- **违反的原理**：{violated_principle_2}（引用位置：{ref_2}）

---

## 四、渐进训练（含 Faded Completion Practice）

> **本节目标**：在理解示范解题的基础上，通过逐步淡出步骤，降低支架，检验你是否真正掌握了解题过程。

### 练习 1：{completion_question_1}

**解题框架**（部分步骤已淡出）：

{step_a} → {step_b} → **___** → **___** → {final_answer}

> 请补全空缺的步骤。
>
> **理由项要求**（操作性/程序性知识点强制；其他类型可省略理由行）：每个空缺后必须追加一行 `**理由**：___`，说明该答案依据哪条原理或规格——这把练习从识记抬升到理解/应用。

**我的答案**：

1. 步骤 a：{answer_a}
   **理由**：{reason_a}
2. 步骤 b：{answer_b}
   **理由**：{reason_b}
3. 步骤 c：{answer_c}
   **理由**：{reason_c}
4. 步骤 d：{answer_d}
   **理由**：{reason_d}

---

### 练习 2：{completion_question_2}

**解题框架**（部分步骤已淡出）：

{step_a} → **___** → {step_c} → **___** → {final_answer}

> 请补全空缺的步骤。
>
> **理由项要求**（同练习 1）：每空缺后追加 `**理由**：___`。

**我的答案**：

1. 步骤 a：{answer_a}
   **理由**：{reason_a}
2. 步骤 b：{answer_b}
   **理由**：{reason_b}
3. 步骤 c：{answer_c}
   **理由**：{reason_c}
4. 步骤 d：{answer_d}
   **理由**：{reason_d}

---

## 五、掌握测试（含新情境题）

> **本节目标**：在全新情境中独立解决问题，检验是否真正掌握而非仅能复现刚看过的范例。
>
> ⚠️ **测试题与训练题不同**：测试题使用了新的情境和表达方式，不会出现"刚看过的原题"。

### 测试题 1：{test_question_1}

[来源：{来源说明}，非本课原例]

**我的答案**：

---

### 测试题 2：{test_question_2}

[来源：{来源说明}，非本课原例]

**我的答案**：

---

### 测试题 3：{test_question_3}

[来源：{来源说明}，非本课原例]

**我的答案**：

---

## 六、掌握度反馈

> 完成掌握测试后，请将文件交给 AI 批改。批改结果将追加到下方。

---

## 七、思考模块（拓展问题 + 知识链条）

> **目的**：把本课孤立知识点"串"起来，发现你自己的盲点。
> **语法约定**（对应设计文档 §九 Q8 决策）：
>   - 关键词用**单反引号**包裹（如 `卷绕机制`），AI 批改时按关键词绑到 `learner_model.concept_mastery`
>   - 代码片段必须用**三引号**代码块包裹（`` ``` ``），不会被当成关键词匹配
>   - 问题越具体越好；"我有点懵"这种模糊描述会被 AI 追问

### 7.1 本课关键词索引（AI 预生成）

> 从元信息 `concept_keywords` 展开。回落规则：在 `settings/glossary.md` 查不到映射时，用 lesson 讲解中出现的原词。

本课涉及的 {N} 个核心关键词：

- {concept_keyword_list}

### 7.2 预生成的关键知识链（启发思考用）

> **生成规则**（对应设计文档 §九 Q3 决策）：
> - 条数按 `concept_tags` 数量动态，**最多 5 条**
> - 每条链中的关键词必须在本课讲解中实际出现过，禁止凭空推导
> - 关系标签用简短中文（如 `超出触发`、`直接后果`、`必须延时`）

```
{chain_1}
{chain_2}
{chain_3}
```

> **格式参考**：
> `页大小` ─(超出触发)→ `卷绕机制` ─(直接后果)→ `内存覆盖`
> `HAL_I2C_Mem_Write` ─(含参数)→ `MemAddress` ─(字节数由)→ `I2C_MEMADD_SIZE_8BIT`

### 7.3 你的问题（软约束，建议至少 1 条）

> 对应设计文档 §九 Q2 决策：**软约束**——跳过不阻塞下一课，但统计上会反映到 `learner_model`。
> 建议用单反引号包裹问题涉及的关键词。

**问题 1**：

**问题 2**（可选）：

**问题 3**（可选）：

### 7.4 你的知识链（可选）

> 用 `概念A` → `概念B` → `概念C` 的形式写出你理解的关系。
> AI 批改时会对比预生成的链与你的链，指出差异。

**我理解的关系**：

---

## 八、Reflection（元认知）

> 职责拆分：内容层问题已移至 §七 思考模块；本节只关注元认知与主观感受（对应设计文档 §五.4）。

完成本节后，请回答：

1. **认知难度** (1-5)：[ ] 1-太简单 [ ] 2-刚好 [ ] 3-有点难 [ ] 4-很困难 [ ] 5-完全不懂
2. **Worked Example 有没有帮助你理解"为什么"？**：
3. **课后对教学方式的其他反馈**（可选）：

---

## 九、本节要点总结（含关键词关系图 · L2）

### 9.1 关键概念关系图（文本树形式）

> 轻量文本树 + 箭头表达；Mermaid 图留给 L3 章节综合图（本模板不包含）。
> **约束**：图中节点必须是 §9.2 详细说明中出现过的关键词——禁止此图凭空新增节点。

```
{concept_tree_with_arrows}
```

> **格式参考**：
>
> ```
> `HAL_I2C_Mem_Write` ─┬── `MemAddress`（设备内部寄存器地址）
>                      ├── `MemAddSize` ← `I2C_MEMADD_SIZE_8BIT`
>                      └── `Timeout`（超时阈值）
>
> `AT24C02` ─→ `页大小(8B)` ─→ 超过 ─→ `卷绕机制` ─→ `内存覆盖`
>                          └→ 写入后 ─→ `写入延时(5ms)`
> ```

### 9.2 详细说明（每条以反引号关键词作为标签）

- **`{keyword_1}`**：{key_point_1}
- **`{keyword_2}`**：{key_point_2}
- **`{keyword_3}`**：{key_point_3}

### 9.3 关键术语（同步回填 glossary）

> **同步规则**（对应设计文档 §九 Q5 决策）：本表每行的 `concept_tag` 必须与元信息 `concept_tags` 一致；
> 新术语同时追入 `settings/glossary.md`（中文关键词 · 英文 · 定义 · 首次出现）。

| 术语 | 定义 | concept_tag |
|------|------|-------------|
| {term_1} | {definition_1} | {concept_tag_1} |
| {term_2} | {definition_2} | {concept_tag_2} |

---

## 十、下一课预告

{next_lesson_preview}

---

## 附录：图表引用

> **路径规则**（详见 `SKILL.md §4.2.1 图表处理规则`）：
>
> - 资料原图：`![{caption}](../images/{hash}.jpg)` → 解析为 `{session_dir}/images/{hash}.jpg`
> - AI 生成图：`![{caption}](../diagrams/{slug}.png)` → 解析为 `{session_dir}/diagrams/{slug}.png`
> - 生成图必须存到 `{session_dir}/diagrams/`，禁止放项目根 `diagrams/`
>
> **引用决策顺序**：
>
> 1. 有资料原图匹配 → 用原图
> 2. 原图质量差 → 原图 + 理解性 DrawIO 并列
> 3. 资料无图且需可视化 → 生成 DrawIO
> 4. 文字/表格可表达 → 不画图

| 图表标题 | 类型 | 引用路径 | 说明 |
|---------|------|---------|------|
| {caption_1} | 资料原图 | `../images/{hash_1}.jpg` | 来自{章节_1} |
| {caption_2} | AI 生成 | `../diagrams/{slug_2}.png` | 理解性示意（同名 `.drawio` 源文件可编辑） |
