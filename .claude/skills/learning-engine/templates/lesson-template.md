# Lesson {index}: {lesson_title}

> **文件名约定**（2026-04-18 新标准 · 详见 `SKILL.md §4.2 命名约定`）：
> - 单页课题：`NN_描述.md`（如 `06_四大总线对比.md`）
> - 多子课题拆分：`NN.X_描述.md`（如 `02.0_I2C 协议原理.md`、`02.1_I2C 协议代码.md`）
> - 旧 session 仍兼容 `lesson_N.md` 格式
> - 文件名写入 `session_state.json.lesson_files[index-1]`，作为权威映射
>
> **占位符约定**（2026-04-18 新增）：
> - `{variable_name}`（具名，如 `{concept_tags}`、`{step_1}`、`{keyword_1}`）：**AI 实例化时必须替换**为本课实际内容
> - `{    }`（4 空白）：**学习者填写槽**，AI 实例化时原样保留，供用户直接写入答案/理由/问题
> - 实例化完成的 lesson 文件中应只保留 `{    }`，**不应残留**任何 `{具名变量}` 形式的未替换占位符

**时间**: {timestamp}
**主题**: {topic_name}
**目标认知层级**: {bloom_level}
**知识类型**: {knowledge_type}
**讲解策略**: {teaching_strategy}
**教学模式**: {teaching_mode}              <!-- A（单场景/知识结构导向）| B（多场景/场景闭环导向）—— 详见 §三 开头决策规则 -->

**概念标签**: {concept_tags}                  <!-- 机器 slug，格式：[{topic}-{concept-name}, ...] -->
**概念关键词**: {concept_keywords}          <!-- 学习者可见词（中文或保留英文），与 concept_tags 严格一一对应顺序一致 -->
**前置依赖**: {prerequisites}

<!-- ↓↓↓ 仅 teaching_mode=B 时填写；A 模式删除下方 scenario_closures 段 ↓↓↓ -->
**场景闭环清单**（仅 B 模式）:
```yaml
scenario_closures:
  - name: {closure_1_name}           # 如 EEPROM
    source_project: {source_project_1}  # 如 18-i2c-eeprom
    source_files:
      - {source_file_1_path}           # 如 Core/Src/eeprom.c
  - name: {closure_2_name}
    source_project: {source_project_2}
    source_files:
      - {source_file_2_path}
```
<!-- ↑↑↑ scenario_closures 段结束 ↑↑↑ -->

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
| {core_question_1} | {    } |
| {core_question_2} | {    } |
| {core_question_3} | {    } |

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
> **教学模式二选一**（2026-04-18 新增 · 详见 `docs/plans/2026-04-18-scenario-closure-feynman-design.md`）：
>
> | 模式 | 元信息 | 适用 | 本节结构 |
> |------|--------|------|---------|
> | **A** | `teaching_mode: A` | 概念性 / 原理性 / 单场景操作性 | 使用下方 `## 三-A` 结构（3.1, 3.2, 3.3 + Worked Example + 反模式画廊） |
> | **B** | `teaching_mode: B` | 多场景操作性（≥ 2 独立可 ship 的场景/外设/模块，如 02.1 的 EEPROM/OLED/AHT20） | 使用下方 `## 三-B` 结构（3.0 全局图景 + 3.1, 3.2, … 场景闭环 + 3.∞ 汇合升维） |
>
> **AI 填充规则**：
> - 读元信息 `teaching_mode` 字段，选择对应下方模式
> - **只保留所选模式的结构**，删除另一模式的整段
> - 生成后的 lesson 文件**不应同时出现 `## 三-A` 和 `## 三-B`**
> - 若 `teaching_mode: B`，必须同时填入 `scenario_closures` 元信息
>
> **代码型知识点附加要求**（知识类型为 `操作性` 或 `程序性` 时强制执行；`概念性` / `原理性` 可省略）：
>
> - 每段 ≥3 行的关键代码块后，必须紧跟一张「代码锚点映射表」（格式见 3.1 示例）
> - Worked Example 之后必须追加「反模式画廊」子节（格式见下方）
> - 渐进训练中的每个空缺必须配「理由项」（格式见 §四）
>
> **代码课正代码 10 项生产级审查清单**（操作性/程序性 Lesson 必须逐项通过；任何一项违反应在反模式画廊中作为"坑位"演示）：
>
> 1. **HAL/SDK 返回值全检查**：每个阻塞式 API 调用 (`HAL_I2C_*`、`HAL_SPI_*`、`HAL_Delay` 等) 的返回值必须被使用（条件判断/return/log），严禁丢弃。
> 2. **缓冲区大小与最大负载匹配**：栈上缓冲区须能容纳该 API 的最大可能负载（如 128×64 OLED 全屏 1024 B 不能用 `uint8_t buf[257]`）；大缓冲区用 `static` 或堆；必要时改用 HAL 的 `Mem_Write` 零栈模式。
> 3. **字节数与数据手册对齐**：读写长度必须与数据手册章节一致（如 AHT20 单次 7 字节含 CRC，而非 6 字节）；在注释中注明手册位置。
> 4. **外设完整性校验不可省**：若外设内置 CRC/校验和（AHT20 CRC-8、BME280 CRC 等），代码必须做校验；不能"读回来不校验直接用"。
> 5. **地址位宽显式声明**：7 位地址用 `(0x50u << 1)` 等形式显式左移，而不是直接写 `0xA0` 魔数；体现"左移是你的责任"的心智模型。
> 6. **时钟/电气下限约束记录**：若依赖某外设参数的下限（如 I2C 100 kHz 要求 APB1 ≥ 2 MHz、SPI CS 建立时间），必须在注释或旁注中明写出来。
> 7. **错误分类而非一刀切**：区分 `HAL_BUSY`（总线忙）、`HAL_TIMEOUT`（超时）、`HAL_ERROR`（NACK/参数错）三种语义，不要统统 `return HAL_ERROR`——调用方失去排查线索。
> 8. **无锁定端口 + 有上限轮询**：任何 `while (flag)` 式轮询必须有超时/重试计数器；防止从机死机导致固件锁死。
> 9. **决策树与代码一致**：若 §3.2 给出 API 选型决策树，§3.3+ 的实际代码**每一处**用哪个 API 都应与决策树分类一致；出现矛盾是严重设计缺陷。
> 10. **反模式来自正代码的影子**：§五 反模式画廊的每个错误，都应是"把正代码某一行移除/改错"所得；反模式不是教学性虚构，而是正代码的"负向镜像"。
>
> 这 10 项是 2026-04-18 `02.1_I2C 协议代码.md` 深度缺陷复盘的总结——每项都有真实踩坑案例背书。新课在生成正代码后、提交前必须逐项过一遍。

<!-- ============================================================ -->
<!-- ====== [模式 A] 开始 · teaching_mode=A 时保留本段 ====== -->
<!-- ====== AI 填充规则：若 teaching_mode=B，删除本段至 ====== -->
<!-- ====== [模式 A] 结束 标记之间的全部内容                ====== -->
<!-- ============================================================ -->

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

<!-- ============================================================ -->
<!-- ====== [模式 A] 结束                                ====== -->
<!-- ============================================================ -->

<!-- ============================================================ -->
<!-- ====== [模式 B] 开始 · teaching_mode=B 时保留本段 ====== -->
<!-- ====== AI 填充规则：若 teaching_mode=A，删除本段至 ====== -->
<!-- ====== [模式 B] 结束 标记之间的全部内容                ====== -->
<!-- ============================================================ -->

### 3.0 全局图景

> **本节目标**（30 秒扫完，不求记住）：建立本课的"地图"——看到 N 个闭环的全貌，理解它们是独立可 ship 的单元，抽出共享基座。

#### 3.0.1 本课 = {N} 个独立闭环

本课将覆盖以下 **{N}** 个**独立可 ship** 的场景闭环：

| # | 场景 | 源码工程 | 关键原理 | Feynman 侧重 |
|---|------|---------|---------|-------------|
| 3.1 | {closure_1_name} | `{source_project_1}` | {key_principle_1} | {feynman_focus_1} |
| 3.2 | {closure_2_name} | `{source_project_2}` | {key_principle_2} | {feynman_focus_2} |
| 3.3 | {closure_3_name} | `{source_project_3}` | {key_principle_3} | {feynman_focus_3} |

> **学习路径**：每环自封闭——学完任一环即可**独立烧板运行**。可按顺序学，也可跳关学感兴趣的先。
>
> **跨环链接在哪里**：§3.∞ 汇合升维——只在 3 环都学完后做"费曼第二轮"。

#### 3.0.2 共享基座：{shared_foundation_title}

> **本节目的**：抽出 N 个闭环都用得到的"底座"知识，后续闭环不重复。

{shared_foundation_content}

**代码锚点映射**（共享基座到原理）：

| 代码/配置 | 对应原理 | 所有闭环使用情况 |
|-----------|---------|----------------|
| `{shared_symbol_1}` | {shared_principle_1} | §3.1 / §3.2 / §3.3 全部使用 |
| `{shared_symbol_2}` | {shared_principle_2} | §3.1 / §3.2 / §3.3 全部使用 |

#### 3.0.3 共享决策树：{decision_tree_title}（单页速查）

> **本节目的**：把"选哪个 API / 用哪个寄存器 / 走哪条路径"的决策压到一页。后续闭环直接引用，不重讲。

```
{decision_tree_content}
```

> **格式参考**（以 I2C API 选型为例）：
>
> ```
> 我要读写的设备 →
>   ├── 有内部寄存器地址？(如 EEPROM/传感器寄存器)
>   │      → YES: 用 `HAL_I2C_Mem_Read/Write`（HAL 自动发 Sr）
>   │      → NO:  下一步
>   └── 是纯字节流？(如 OLED 命令/数据 / AHT20 命令序列)
>          → 写：`HAL_I2C_Master_Transmit`
>          → 读：`HAL_I2C_Master_Receive`
> ```

---

### 3.1 {closure_1_name} 闭环

> **本闭环目标**：读完本环，你能**独立打开** `{source_project_1}` 工程烧板运行，并理解每一行为什么这样写。

#### 3.1.1 📖 场景（≤ 50 字）

> **场景描述**：{scenario_1_description}
>
> **硬件清单**：{hardware_list_1}
> **预期效果**：{expected_behavior_1}
> **为什么学这个**：{why_learn_1}（回答"学完能解决什么实际问题"）

#### 3.1.2 💻 完整可运行代码（精瘦模式）

> **源码来源**：`{source_code_root}/{source_project_1}/{source_file_1_path}`（行 {line_range_1}）
> **HAL 版本**：{hal_version_1}
> **下方为 happy path 核心片段**（30-50 行）；完整文件请打开 Keil 工程查看。

```{language_1}
{core_code_snippet_1}
```

> **未展示部分**（同一文件其他行）：
> - 行 {omitted_range_1_a}：{omitted_description_1_a}
> - 行 {omitted_range_1_b}：{omitted_description_1_b}
>
> **配套文件**：
> - `{companion_file_1_a}`：{companion_description_1_a}
> - `{companion_file_1_b}`：{companion_description_1_b}

#### 3.1.3 🔍 逐部分解释（行号锚点，不重述代码）

| 行号 | 代码段 | 作用 | 原理对应 |
|------|-------|------|---------|
| {line_ref_1_a} | `{code_fragment_1_a}` | {purpose_1_a} | §3.1.4.{sub} {principle_ref_1_a} |
| {line_ref_1_b} | `{code_fragment_1_b}` | {purpose_1_b} | §3.1.4.{sub} {principle_ref_1_b} |
| {line_ref_1_c} | `{code_fragment_1_c}` | {purpose_1_c} | §3.0.2 {shared_principle_ref_1_c} |
| {line_ref_1_d} | `{code_fragment_1_d}` | {purpose_1_d} | §3.1.4.{sub} {principle_ref_1_d} |

> **禁止**：在本节重复粘贴代码片段；所有讲解以行号锚定 §3.1.2 的代码。

#### 3.1.4 🧠 原理剖析（侧重 {closure_1_name} 使用的原理）

> **范围约束**：只讲本闭环**用到的**原理。跨闭环共享的原理（如 HAL 8 位地址约定）首次在本环讲清，后续闭环仅引用。

##### 3.1.4.1 {principle_1_1_title}

{principle_1_1_explanation}

**反事实**：若不遵守此原理 → {counterfactual_1_1}。

##### 3.1.4.2 {principle_1_2_title}

{principle_1_2_explanation}

**反事实**：若不遵守此原理 → {counterfactual_1_2}。

##### 3.1.4.3 {principle_1_3_title}（可选）

{principle_1_3_explanation}

#### 3.1.5 🎯 渐进训练（基于 §3.1.2 代码变形）

> **范围**：所有练习都基于 §3.1.2 代码变形——让学员从"看懂代码"上升到"改对代码"。

**练习 1**：{exercise_1_1_question}

{exercise_1_1_frame}

**我的答案**：

{    }

<details>
<summary><b>💡 点开查看参考答案</b></summary>

- **[核心结果]**：{exercise_1_1_answer_core}
- **[推导过程]**：{exercise_1_1_answer_reasoning}
- → **深度洞察**：{exercise_1_1_insight}

</details>

---

**练习 2**：{exercise_1_2_question}

{exercise_1_2_frame}

**我的答案**：

{    }

<details>
<summary><b>💡 点开查看参考答案</b></summary>

- **[核心结果]**：{exercise_1_2_answer_core}
- **[推导过程]**：{exercise_1_2_answer_reasoning}
- → **深度洞察**：{exercise_1_2_insight}

</details>

#### 3.1.6 🔴 Feynman 输出（B 档 · 三选二，至少完成 2 项）

> **硬约束**：跳过 Feynman **不能**进入下一闭环。AI 批改覆盖度 < 60% 会引导你回 §3.1.3 / §3.1.4 重读。
>
> **为什么要做这步**：费曼学习法的核心是"输出倒逼输入"——你以为你懂了，但只有自己讲一遍、画一遍、写一遍，才能发现盲点。

---

**选项 a · 文字小结**（≤ 80 字硬限）

用自己的话写出 "`{closure_1_name}` 驱动的 5 要素"——注意是 **你的话**，不是抄课文：

```
1. {    }
2. {    }
3. {    }
4. {    }
5. {    }
```

> **AI 批改点**：覆盖度（是否包含 5 个关键概念）+ 独立性（是否抄课文）+ 准确度（是否说错）。

---

**选项 b · 手绘拍照**（推荐 · 最高强度 Feynman）

任选**一幅**图手绘，拍照保存到 `{lesson_file_stem}_notes/photos/`：

- **b1**：{diagram_suggestion_1_1}（如 {closure_1_name} 时序图——SDA/SCL 波形 + 字节标记）
- **b2**：{diagram_suggestion_1_2}（如 {closure_1_name} 内存/地址空间示意）
- **b3**：{diagram_suggestion_1_3}（如 {closure_1_name} 状态机）

> **拍照路径约定**：
> ```
> learning-history/{topic}/lessons/{lesson_file_stem}_notes/photos/{YYYY-MM-DD}_{closure_slug_1}_{option_slug}.jpg
> ```
> 例：`2026-04-18_eeprom_timing.jpg`
>
> **AI 批改点**：图中关键信号/标记是否画对（`S`、`ADDR`、`DATA`、`A`、`P`、`Sr` 等）；布局是否清晰；有无遗漏关键阶段。

---

**选项 c · 代码改写**（高强度 · 推荐给已烧板过一次的学员）

把 §3.1.2 原版代码改写为 "**{enhancement_requirement_1}**" 版本，保存到 `{lesson_file_stem}_notes/exercises/{closure_slug_1}_safe.{ext}`：

**函数签名**：

```{language_1}
{function_signature_1}
```

**实现要求**：

1. {requirement_1_1}
2. {requirement_1_2}
3. {requirement_1_3}
4. {requirement_1_4}（可选）

> **AI 批改点**：静态分析你的代码 vs 参考实现；检查是否落实本闭环的 10 项审查清单（§三开头）；指出缺失的边界处理。

#### 3.1.7 🔵 闭环检查 + 独特笔记

> **闭环检查**：AI 对你 §3.1.6 的 Feynman 输出做针对性反馈（不是给标准答案，而是**指出盲点 + 给出回读范围**）。

**AI 批改结果**（完成 §3.1.6 后由 AI 追加）：

{ai_feynman_review_1_placeholder}

**是否通过本闭环检查**（AI 判定）：

- [ ] ✅ 通过（覆盖度 ≥ 80%）→ 进入 §3.2
- [ ] ⚠️ 有盲点（60-80%）→ 可选择回读 `{gap_sections}` 或继续（记入 review_queue）
- [ ] ❌ 未通过（< 60%）→ 回读 `{gap_sections}` 后重做 Feynman

---

**你的独特笔记**（追加到 `{lesson_file_stem}_notes/my_notes.md`）：

> 笔记是**你的第二大脑**——下次复习以笔记为主、课文为辅。

```markdown
## §3.1 {closure_1_name} 闭环学到的

**3 个"啊原来如此"的时刻**：
1. ...
2. ...
3. ...

**我最容易错的 1 个点 + 如何避免**：
- 错：...
- 改：...
- 根因：...

**跨章节链接**：
- 联想到之前：`{可能的前课概念}`
- 预感到之后：`{可能的后续课应用}`
```

> **禁止**：把 AI 讲解原样复制粘贴到 my_notes.md——那不是"你的"笔记，费曼学习法无效。

---

### 3.2 {closure_2_name} 闭环

> **说明**：本闭环结构与 §3.1 **同构**，AI 实例化时按 §3.1 的 7 个子节（3.2.1 - 3.2.7）展开。
>
> **与 §3.1 的差异**：侧重 {closure_2_diff_focus}；新出现的原理是 {closure_2_new_principles}；**已在 §3.1 讲过的共享原理直接引用即可**，不重复展开。

{closure_2_content_placeholder}

---

### 3.3 {closure_3_name} 闭环

> **说明**：本闭环结构与 §3.1 **同构**，AI 实例化时按 §3.1 的 7 个子节（3.3.1 - 3.3.7）展开。
>
> **与前两环的差异**：侧重 {closure_3_diff_focus}；新出现的原理是 {closure_3_new_principles}。

{closure_3_content_placeholder}

---

### 3.∞ 汇合升维（费曼第二轮）

> **本节目标**：把 {N} 个独立闭环"升维"成体系认知——**不再重述单环细节，专注跨环共性**。

#### 3.∞.1 跨环对比表（学员先填，AI 再批）

**我的对比表**：

| 特性 | {closure_1_name} | {closure_2_name} | {closure_3_name} |
|------|---|---|---|
| {comparison_axis_1} | {    } | {    } | {    } |
| {comparison_axis_2} | {    } | {    } | {    } |
| {comparison_axis_3} | {    } | {    } | {    } |
| {comparison_axis_4} | {    } | {    } | {    } |

<details>
<summary><b>💡 点开查看参考答案</b></summary>

| 特性 | {closure_1_name} | {closure_2_name} | {closure_3_name} |
|------|---|---|---|
| {comparison_axis_1} | {answer_1_1} | {answer_1_2} | {answer_1_3} |
| {comparison_axis_2} | {answer_2_1} | {answer_2_2} | {answer_2_3} |
| {comparison_axis_3} | {answer_3_1} | {answer_3_2} | {answer_3_3} |
| {comparison_axis_4} | {answer_4_1} | {answer_4_2} | {answer_4_3} |

→ **深度洞察**：{cross_closure_insight}

</details>

#### 3.∞.2 复述决策树（费曼第二轮）

> **任务**：不看 §3.0.3，用**自己的话**复述"{decision_tree_title}"的决策逻辑。

**我的复述**：

{    }

<details>
<summary><b>💡 点开查看参考答案</b></summary>

{decision_tree_restatement_answer}

→ **对比 §3.0.3**：{diff_commentary}（学员复述 vs 原版决策树差异点，可能是简化/盲点/换角度）

</details>

#### 3.∞.3 本课概念图（手绘或 Mermaid，二选一）

> **任务**：把本课涉及的所有概念节点用**你自己的方式**画出关系图——这是全课最高强度的 Feynman 输出。

**选项 A · 手绘拍照**：保存到 `{lesson_file_stem}_notes/photos/{YYYY-MM-DD}_concept_map.jpg`

**选项 B · Mermaid 代码**：在 `{lesson_file_stem}_notes/my_notes.md` 的 §3.∞.3 节写入 Mermaid 图：

```mermaid
graph TD
    {请画出你理解的节点和关系}
```

> **AI 批改点**（完成后由 AI 追加）：
> - 节点覆盖度（是否覆盖本课主要概念）
> - 关系准确度（箭头方向/语义是否正确）
> - 层次清晰度（是否有"物理层/协议层/API 层"这样的分层结构）

#### 3.∞.4 你的疑问（路由到 §七 思考模块）

> 学完 {N} 个闭环后，你对 "{topic}" 还有什么未解决的问题？
>
> 在 §七 思考模块 §7.3 填写——用**单反引号**包裹涉及的关键词。

<!-- ============================================================ -->
<!-- ====== [模式 B] 结束                                ====== -->
<!-- ============================================================ -->

---

## 四、渐进训练（含 Faded Completion Practice）

> **本节目标**：在理解示范解题的基础上，通过逐步淡出步骤，降低支架，检验你是否真正掌握了解题过程。
>
> **模式 B 下的本节定位**：若 `teaching_mode=B`，单闭环的训练已在 §3.X.5 完成；**本节改为 "跨环迁移练习" 1-2 题**（考察共性识别，而非单闭环细节）。模式 A 不受影响，按原练习 1 / 练习 2 结构走。
>
> **参考答案折叠格式规范**（§四/§五 所有练习与测试题必须附上，采用 `<details>` 折叠块）：
>
> ```markdown
> **我的答案**：
>
> 1. {    }
> 2. {    }
>
> <details>
> <summary><b>💡 点开查看参考答案</b></summary>
>
> 1. **[核心结果]**：...
> 2. **[推导过程]**：...（不仅给答案，还要复现思路）
>
> → **深度洞察**：...（引导学员理解本题的元问题 / 跨章节链接）
>
> → **自检**（对填空类题可选）：...（对比学员可能的错误写法）
>
> </details>
> ```
>
> 折叠默认关闭——学员先独立思考，再自查；主流渲染器（GitHub / VSCode / Typora / Obsidian）原生支持。

### 练习 1：{completion_question_1}

**解题框架**（部分步骤已淡出）：

{step_a} → {step_b} → **___** → **___** → {final_answer}

> 请补全空缺的步骤。
>
> **理由项要求**（操作性/程序性知识点强制；其他类型可省略理由行）：每个空缺后必须追加一行 `**理由**：___`，说明该答案依据哪条原理或规格——这把练习从识记抬升到理解/应用。

**我的答案**：

1. 步骤 a：{    }
   **理由**：{    }
2. 步骤 b：{    }
   **理由**：{    }
3. 步骤 c：{    }
   **理由**：{    }
4. 步骤 d：{    }
   **理由**：{    }

---

### 练习 2：{completion_question_2}

**解题框架**（部分步骤已淡出）：

{step_a} → **___** → {step_c} → **___** → {final_answer}

> 请补全空缺的步骤。
>
> **理由项要求**（同练习 1）：每空缺后追加 `**理由**：___`。

**我的答案**：

1. 步骤 a：{    }
   **理由**：{    }
2. 步骤 b：{    }
   **理由**：{    }
3. 步骤 c：{    }
   **理由**：{    }
4. 步骤 d：{    }
   **理由**：{    }

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
> **排版**：遵循 `SKILL.md §4.2 排版可读性规则 #8`——协议标识符/技术术语（`S`、`ADDR`、`ACK`、寄存器名、API 签名等）一律用**英文**保持字符对齐；中文注释/段名放图的正下方或节点后的括号内，不塞进箭头链中。

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

---

## 附录 B：精瘦源码引用格式（仅 `teaching_mode=B`）

> **适用**：`teaching_mode=B` 且 `settings/background.md` 配置了 `source_code_root`。
> **来源**：`docs/plans/2026-04-18-scenario-closure-feynman-design.md §五`。

### B.1 引用块标准格式

每个场景闭环的 §X.2 "完整可运行代码" 节必须遵守：

```markdown
> **源码来源**：`{source_code_root}/{project}/{file_path}`（行 {start}-{end}）
> **HAL 版本**：{version}
> **下方为 happy path 核心片段（30-50 行）**；完整文件请打开工程查看。

```{language}
{30-50 行的核心代码}
```

> **未展示部分**（同一文件其他行）：
> - 行 {range}：{description}
> - 行 {range}：{description}
>
> **配套文件**：
> - `{sibling_file}`：{description}
```

### B.2 硬约束

- ❌ 禁止粘贴 > 60 行的单段源码
- ❌ 禁止粘贴 CubeMX 生成的 msp/it/hal_conf 等模板文件
- ❌ 禁止隐匿源码来源（必须标注 `{file}:{start}-{end}`）
- ❌ 禁止 "修改原版后冒充原版"（增强版必须显式标注）
- ✅ 精瘦模式以 **核心 30-50 行 + 未展示段说明 + delta 对比** 为主

### B.3 Delta 分析格式（§X.4 原理剖析中使用）

当原版代码与 "§三开头 10 项生产级审查清单" 有 gap 时，以并列表展示：

```markdown
##### {原理标题}

**原版 `{file}:{line_range}`**：
```{language}
{原版关键片段}
```

**生产增强版**（若引入审查清单第 N 项）：
```{language}
{增强版关键片段}  // ← 区别：{具体增强点}
```

**为什么**：{原版省略此项的工程取舍} / {增强版防止的失败模式}。
```

---

## 附录 C：独特笔记 `my_notes.md` 模板（仅 `teaching_mode=B`）

> **适用**：`teaching_mode=B`。每课配套一个 `{lesson_file_stem}_notes/` 目录。
> **来源**：`docs/plans/2026-04-18-scenario-closure-feynman-design.md §六`。

### C.1 目录结构

```
learning-history/{topic}/lessons/
├── {lesson_file_stem}.md                  ← 主课文（AI 生成 · 本模板实例化产物）
└── {lesson_file_stem}_notes/              ← 学员笔记目录（本课独立）
    ├── my_notes.md                         ← 主笔记（学员填 + AI 追加批改）
    ├── photos/                             ← 手绘拍照（Feynman 选项 b）
    │   ├── {YYYY-MM-DD}_{closure}_timing.jpg
    │   ├── {YYYY-MM-DD}_{closure}_memmap.jpg
    │   └── {YYYY-MM-DD}_concept_map.jpg
    └── exercises/                          ← 代码改写（Feynman 选项 c）
        ├── {closure_1}_safe.c
        ├── {closure_2}_safe.c
        └── {closure_3}_safe.c
```

### C.2 `my_notes.md` 初始模板

> **生成时机**：课程启动本课时，AI 创建此文件骨架；学员每完成一闭环的 §X.6 Feynman 后填入对应节。
> **保留约定**：空槽用 `{    }`（4 空白）；AI 批改追加到 "AI 批改反馈" 子节。

```markdown
# {lesson_title} · 我的笔记

**最后更新**：{YYYY-MM-DD HH:mm}
**主课文**：`../{lesson_file_stem}.md`
**本笔记定位**：你的第二大脑。下次复习时以本文件为主、课文为辅。

---

## §3.1 {closure_1_name} 闭环学到的

### Feynman 输出（三选二）

**a · 5 要素**：
1. {    }
2. {    }
3. {    }
4. {    }
5. {    }

**b · 手绘**：见 `photos/{YYYY-MM-DD}_{closure_1_slug}_{type}.jpg`

**c · 代码改写**：见 `exercises/{closure_1_slug}_safe.c`

### AI 批改反馈

{ai_review_for_closure_1_placeholder}

### 我的独特笔记

**3 个"啊原来如此"的时刻**：
1. {    }
2. {    }
3. {    }

**我最容易错的 1 个点 + 如何避免**：
- 错：{    }
- 改：{    }
- 根因：{    }

**跨章节链接**：
- 联想到之前：`{    }`
- 预感到之后：`{    }`

---

## §3.2 {closure_2_name} 闭环学到的

{同 §3.1 结构}

---

## §3.3 {closure_3_name} 闭环学到的

{同 §3.1 结构}

---

## §3.∞ 汇合升维

### 跨环对比表（我的版本）

| 特性 | {closure_1_name} | {closure_2_name} | {closure_3_name} |
|------|---|---|---|
| {    } | {    } | {    } | {    } |
| {    } | {    } | {    } | {    } |

### API 选型决策树（我的复述）

{    }

### 本课概念图

见 `photos/{YYYY-MM-DD}_concept_map.jpg` 或下方 Mermaid：

```mermaid
graph TD
    {    }
```

### 我对本课的疑问（与 §七思考模块同步）

1. `{    }`：{    }
2. `{    }`：{    }
```

### C.3 笔记演化机制

- 学员**每完成 1 个闭环的 Feynman 输出**，在对应节填入（a/b/c 三选二）
- AI 批改后追加到 "AI 批改反馈" 子节（不覆盖学员原文）
- 学员在 "我的独特笔记" 节填入个人感悟——**禁止复制 AI 讲解**
- 课程结束后，此文件是学员复习的**主入口**（比主课文更高效，因为是"自己的话"）
- 后续 L4 专题综合图生成时可抽取 "跨章节链接" 段作为补充输入
