# 难度适配功能实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 learning-engine 中增加前置知识诊断流程和大测驗体系，使课程难度与用户实际水平匹配。

**Architecture:** 在现有 pipeline 的 Step 3 末尾插入 Step 3.5（课前诊断），独立新增大测驗模块。诊断结果持久化到 background.md，影响后续所有 Lesson 的生成。大测驗一次性建立知识图谱，诊断做局部微调。

**Tech Stack:** Python, Markdown templates, JSON (session_state), Claude Code SKILL.md 格式

---

## Chunk 1: 模板与示例文件（无行为变更）

### Files

- Create: `.claude/skills/learning-engine/templates/prereq-diagnostic-template.md`
- Create: `.claude/skills/learning-engine/templates/prereq-diagnostic-recheck-template.md`
- Create: `.claude/skills/learning-engine/templates/remediation-lesson-template.md`
- Create: `settings/prerequisite-map.example.md`
- Create: `settings/topic-knowledge-map.example.md`
- Modify: `settings/background.example.md`（新增诊断历史字段示例）
- Modify: `.claude/skills/learning-engine/SKILL.md`（Resource Manifest 表格新增模板引用）

---

### Chunk 1.1: prereq-diagnostic-template.md

- [ ] **Step 1: 创建文件**

路径: `.claude/skills/learning-engine/templates/prereq-diagnostic-template.md`

```markdown
# 课前诊断 — Lesson {index}: {lesson_title}

> 本诊断用于检测学习本课所需的前置知识掌握情况。
> 预计耗时：{estimated_time}

**诊断模式**：{quick / full}
**前置知识缺口**：{gap_1}、{gap_2}、{gap_3}

---

## 开始诊断

> 请在每道题的"我的答案"区域填写答案。

### 诊断题 {N}: {concept_name}

{question_content}

**前置知识点**：{related_concept}
**来源提示**：{source_hint}

**我的答案**：

---
```

- [ ] **Step 2: 验证文件创建**

Run: `ls .claude/skills/learning-engine/templates/prereq-diagnostic-template.md`
Expected: 文件存在

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/learning-engine/templates/prereq-diagnostic-template.md
git commit -m "feat(templates): add prereq-diagnostic-template.md"
```

---

### Chunk 1.2: prereq-diagnostic-recheck-template.md

- [ ] **Step 1: 创建文件**

路径: `.claude/skills/learning-engine/templates/prereq-diagnostic-recheck-template.md`

```markdown
# 课前诊断（复诊）— Lesson {index}: {lesson_title}

> 复诊目的：验证前置补救课（{gap_name}）是否已真正掌握。
> 预计耗时：3 分钟（快速模式 3 题）

**原诊断掌握度**：{original_percentage}%
**已完成的补救课**：{gap_1}、{gap_2}、...

---

## 开始复诊

> 请在每道题的"我的答案"区域填写答案。

### 复诊题 {N}: {concept_name}

{question_content}

**前置知识点**：{related_concept}

**我的答案**：

---
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/learning-engine/templates/prereq-diagnostic-recheck-template.md
git commit -m "feat(templates): add prereq-diagnostic-recheck-template.md"
```

---

### Chunk 1.3: remediation-lesson-template.md

- [ ] **Step 1: 创建文件**

路径: `.claude/skills/learning-engine/templates/remediation-lesson-template.md`

```markdown
# 前置补救课：{gap_concept_name}

> 本课为 Lesson {index}（{lesson_title}）的前置铺垫课，
> 用于填补诊断中暴露的知识缺口。

**诊断触发**：前置诊断掌握度 {percentage}%（{wrong_count} 题错误）
**涉及前置缺口**：{gap_1}、{gap_2}、...

---

## 学习目标

1. 能用自己的话说出 {gap_concept} 是什么
2. 能举出一个生活中的例子说明其作用
3. 为 Lesson {index} 的新知识扫清概念障碍

---

## 讲解内容

### {gap_concept_name} 是什么

> **类比**：{用生活化的类比让概念具象化}
>
> **定义**：{给出简洁的正式定义}
>
> **与本课的关系**：{一句话说明为什么学这个有助于理解下一课}

---

## 诊断反馈练习

> 完成本课后，回顾诊断题中的错题，看是否能重新回答。

### 练习 1

{围绕缺失的前置知识点设计 1-2 题，难度 Bloom L1-L2}

**我的答案**：

---

## 本节要点

- {concept_1}
- {concept_2}
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/learning-engine/templates/remediation-lesson-template.md
git commit -m "feat(templates): add remediation-lesson-template.md"
```

---

### Chunk 1.4: prerequisite-map.example.md

- [ ] **Step 1: 创建文件**

路径: `settings/prerequisite-map.example.md`

```markdown
# 前置知识依赖表示例

> 此文件为示例。实际使用时，复制为 `prerequisite-map.md` 并根据具体专题填充。
> 格式：`知识点 | 前置依赖1, 前置依赖2, ...`
> 系统会自动递归展开所有依赖链直到叶子节点。

| 知识点 | 前置依赖 |
|--------|---------|
| SPI CPOL/CPHA | 时钟信号, 串行通信基础 |
| CAN 总线 | SPI 协议原理 |
| 嵌入式操作系统 | C 语言指针, 中断机制 |
| DMA 传输 | 总线架构基础 |
| 时钟信号 | 数字电路基础 |
| 数字电路基础 | 电平概念（高电平/低电平） |
```

- [ ] **Step 2: Commit**

```bash
git add settings/prerequisite-map.example.md
git commit -m "feat(settings): add prerequisite-map.example.md"
```

---

### Chunk 1.5: topic-knowledge-map.example.md

- [ ] **Step 1: 创建文件**

路径: `settings/topic-knowledge-map.example.md`

```markdown
# 知识点覆盖清单示例

> 此文件为示例。实际使用时，复制为 `topic-knowledge-map.md` 并根据具体专题填充。
> 标注规则：
> - ★ 核心知识点：需要人工精制题目（每点 3 题 L1+L2+L3）
> - ○ 边缘知识点：由系统自动生成（每点 2 题 L1+L2）

## I2C 协议

### 物理层 ★（核心，人工题）
  - SDA/SCL 线的作用 ★
  - 上拉电阻的原理 ★
  - 开漏输出的意义 ★
  - 多主机仲裁基础 ○（边缘，自动生成）

### 协议层
  - 起始与停止信号 ★
  - 数据有效性 ★
  - 7位地址与R/W位 ★
  - ACK/NACK 机制 ★
  - 复合读写时序 ★

## SPI 协议

### 时钟系统 ★（核心，人工题）
  - CPOL（时钟极性）★
  - CPHA（时钟相位）★
  - 四种模式对比 ★
  - 采样沿与移位沿 ★

### 数据传输
  - 全双工通信原理 ○
  - 移位寄存器机制 ○
  - W25Q32 Flash 读写流程 ★

## CAN 总线
## RS485 总线
```

- [ ] **Step 2: Commit**

```bash
git add settings/topic-knowledge-map.example.md
git commit -m "feat(settings): add topic-knowledge-map.example.md"
```

---

### Chunk 1.6: background.example.md 新增诊断字段

- [ ] **Step 1: 读取现有文件**

Run: `cat settings/background.example.md`

- [ ] **Step 2: 添加诊断历史区域**

在文件末尾追加：

```markdown
---

## 诊断历史与薄弱知识点

### 当前会话诊断记录

| 日期 | Lesson | 模式 | 掌握度 | 结果 | 暴露缺口 |
|------|--------|------|--------|------|---------|
| 示例日期 | Lesson N (主题) | 快速/完整 | 66.7% | ✅通过/⚠️快速回顾/❌补救课 | 知识点1, 知识点2 |

### 薄弱知识点（长期追踪）

| 知识点 | 出错次数 | 最近触发 | 状态 |
|--------|---------|---------|------|
| 示例薄弱知识点 | 2 | 示例日期 | 🔄刚补救/⚠️弱 |

### 备注

- 用户学习风格：需要大量直觉类比，对抽象定义接受速度较慢
- 建议：涉及硬件时钟/电平时，优先用生活类比引入
- Bloom 层级调整：当前下调至 L2（连续 2 次补救课触发）

### 知识图谱摘要

> 大测驗完成后，知识图谱完整内容存入 `learning-history/{topic}_assessment/knowledge_map.md`。
> 此处仅保存摘要。

| 专题 | 测驗日期 | ✅已掌握 | ⚠️需巩固 | ❌未掌握 |
|------|---------|---------|---------|---------|
| 示例专题 | 示例日期 | 58% | 27% | 15% |
```

- [ ] **Step 3: Commit**

```bash
git add settings/background.example.md
git commit -m "feat(settings): add diagnostic history fields to background.example.md"
```

---

### Chunk 1.7: SKILL.md Resource Manifest 更新

- [ ] **Step 1: 读取 SKILL.md 的 Resource Manifest 区域（大约 line 107-138）**

Run: `sed -n '107,138p' .claude/skills/learning-engine/SKILL.md`

Expected output:
```
### Templates

| Index | Path | Purpose |
|-------|------|---------|
| Lesson 模板 | ... |
...
```

- [ ] **Step 2: 在模板表格末尾追加新模板行**

在 `| 指标模板 | ... | 会话事件日志 |` 之后追加：

```markdown
| 诊断模板 | `${SKILL_DIR}/templates/prereq-diagnostic-template.md` | 课前诊断文件生成模板 |
| 复诊模板 | `${SKILL_DIR}/templates/prereq-diagnostic-recheck-template.md` | 补救课后复诊文件模板 |
| 补救课模板 | `${SKILL_DIR}/templates/remediation-lesson-template.md` | 前置补救课内容模板 |
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/learning-engine/SKILL.md
git commit -m "feat(skill): update Resource Manifest with new diagnostic templates"
```

---

## Chunk 2: Step 3.5 课前诊断核心逻辑

### Files

- Modify: `.claude/skills/learning-engine/SKILL.md`（在 Step 3 末尾插入 Step 3.5）

---

### Chunk 2.1: Step 3.5 整体框架

- [ ] **Step 1: 读取 Step 3 的 CHECKPOINT 位置**

Run: `grep -n "## ✅ Step 3 Complete" .claude/skills/learning-engine/SKILL.md`

Expected: 找到 Step 3 的 CHECKPOINT 行号（约 line 340 附近）

- [ ] **Step 2: 在 Step 3 CHECKPOINT 之后、Step 4 之前插入 Step 3.5**

在 `## ✅ Step 3 Complete` CHECKPOINT 之后、`### Step 4:` 之前插入以下内容：

```markdown
---

### Step 3.5: 课前诊断（Pre-Assessment）

🚧 **GATE**: Step 3 complete；学习目录存在，当前 lesson index 已确定；用户背景已加载。

> **前置说明**：此步骤用于在学习新 Lesson 之前检测用户是否具备所需的前置知识。
> 若诊断通过（掌握度 ≥ 60%），直接进入 Step 4。
> 若诊断未通过，插入前置补救课，确保前置缺口填补后再进入主课。

🛠️ **EXECUTION**:

**3.5.1 前置知识缺口分析（自动 + 手动）**：

1. **递归依赖链展开**：读取 `settings/prerequisite-map.md`（若存在），对下一课涉及的核心概念递归展开依赖链：
   - 从下一课 Lesson 内容草稿中提取关键术语列表
   - 对每个术语，查询 prerequisite-map 中是否有前置依赖
   - 若有，递归查询直到叶子节点（无更早依赖的概念）
   - 与 roadmap_status.md 中已标记为"✅ 已完成"的知识点比对
   - 已在 roadmap 中完成的概念不标记为缺口
2. **自动检测**：对下一课草稿中出现的术语，若在已学课程中从未出现，标记为潜在前置缺口
3. **合并去重**：合并自动检测 + prerequisite-map 手动标注的结果，按依赖链深度排序（叶子先补）

**3.5.2 诊断模式选择（Non-BLOCKING 询问）**：

在对话中非阻塞发送：

```
📋 Lesson {index} 课前诊断

请选择诊断模式：
- 快速模式（3题，约3分钟）— 适合时间紧张或复诊
- 完整模式（8题，约10分钟）— 适合首次学习新专题
- 直接跳过（不推荐）— 有前置知识缺口风险

若未选择，默认使用完整模式。
```

用户可直接回复选择，或说"跳过"、或说"做大测驗"进入大测驗流程。

**3.5.3 生成诊断小测**：

1. 读取 `${SKILL_DIR}/templates/prereq-diagnostic-template.md`
2. 根据前置知识缺口列表生成诊断题：
   - **快速模式**：按优先级选择 3 个概念（核心依赖最强 > 历史薄弱点 > 依赖链深度最深）
   - **完整模式**：为所有检测到的前置缺口各生成 1 题
3. 题目从下一课的学习资料中**反向提取**——从资料讲解段落中提炼前置问题
4. 写入 `${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/lessons/prereq_diagnostic.md`

**3.5.4 诊断通知（Non-BLOCKING）**：

```
📋 Lesson {index} 课前诊断已生成！

📄 文件位置：`./learning-history/${topic_name}_${timestamp}/lessons/prereq_diagnostic.md`

⏱️ 预计耗时：{3分钟 / 10分钟}

📊 前置知识缺口检测到 {N} 个：
  - {concept_1}
  - {concept_2}
  - ...

请阅读诊断文件，完成后告诉我"诊断完成"。
```

⛔ **BLOCKING**：等待用户说"诊断完成"或选择跳过。

**3.5.5 批改与判定**：

1. 读取 `prereq_diagnostic.md`，提取"我的答案"区域
2. 三档评估（沿用 Step 4.3 框架）：
   - **✅ 完全正确**：结论对 + 推理完整（1.0 分）
   - **⚠️ 部分正确**：结论对但答偏/推理有瑕疵，知识点实质正确（0.5 分）
   - **❌ 错误**：结论错误或完全不知道（0.0 分）
3. **掌握度计算**：
   ```
   掌握度 = (完全正确题数 × 1.0 + 部分正确题数 × 0.5) / 总题数 × 100%
   ```
4. **判定路由**：
   | 掌握度 | 结果 | 行动 |
   |--------|------|------|
   | ≥ 60% | ✅ 通过 | 直接进入 Step 4 |
   | 33% ≤ x < 60% | ⚠️ 部分通过 | Step 4 生成主课，开头加快速回顾 |
   | < 33% | ❌ 未通过 | 插入前置补救课(s) |
5. 将批改结果写入 `prereq_diagnostic.md` 底部

**3.5.6 Bloom 层级动态下调（与 Step 4.4 联动）**：

读取 `background.md` 中"备注"区域的 Bloom 层级调整记录：
- 若本次诊断触发了补救课，累加"连续补救课计数"
- 若连续 2 次诊断都触发了补救课，在 background.md 的"备注"中追加：
  ```
  - Bloom 层级调整：当前下调至 L2（连续 2 次补救课触发）
  ```
- Step 4.4 的升级/降级触发阈值也相应调整：
  - 正常情况：连续两课全部答对 → 升级
  - Bloom 下调后：连续三课全部答对 → 升级，并可恢复一级层级

✅ **CHECKPOINT**:
```markdown
## ✅ Step 3.5 Complete
- [x] 前置知识缺口分析完成：{N} 个缺口（{depth} 层依赖链）
- [x] 诊断模式：{quick / full}
- [x] 批改完成：掌握度 {percentage}%
- [x] 判定结果：{通过 / 部分通过 / 未通过}
- [ ] **Next**: auto-proceed based on result:
     ✅ 通过 → Step 4（主课 Lesson 生成）
     ⚠️ 部分通过 → Step 4 + 快速回顾
     ❌ 未通过 → Step 3.5.7（插入补救课）
```

---

### Chunk 2.2: Step 3.5.7 补救课插入 + 闭环流程

在 Step 3.5 CHECKPOINT 之后、Step 4 之前，追加：

```markdown
**3.5.7 前置补救课插入 + 闭环**：

**触发条件**：3.5.5 判定结果为"❌ 未通过"（掌握度 < 33%）

🛠️ **EXECUTION**：

1. **生成前置补救课**（每个前置缺口单独一个）：
   - 读取 `${SKILL_DIR}/templates/remediation-lesson-template.md`
   - 按依赖链顺序（叶子先补）生成 `lesson_{index}_prereq_{gap_name}.md`
   - 每个补救课聚焦单一概念，5-8 分钟阅读量，使用"动机铺垫 → 核心定义 → 直觉类比"策略
   - 补救课**不更新** `session_state.json` 的 `current_lesson`，**不计入** roadmap 的主线进度
   - 在 `roadmap_status.md` 的"学习历史"表格中追加补救课记录（标注为 `🔧 补救课`）

2. **通知用户补救课已生成**：
   ```
   🔧 前置补救课已生成（{count} 节）

   📄 文件位置：
   {gap_1} → ./learning-history/{topic}_{timestamp}/lessons/lesson_{index}_prereq_{gap_1}.md
   {gap_2} → ./learning-history/{topic}_{timestamp}/lessons/lesson_{index}_prereq_{gap_2}.md
   ...

   请依次阅读补救课，完成后告诉我"补救课完成"。
   ```

⛔ **BLOCKING**：等待用户说"补救课完成"或"做完了"。

3. **补救课批改（轻量）**：
   - 读取补救课文件，评估用户练习答案（不严格计分，只需确认用户有作答）
   - 若用户未作答，提示先去文件中填写

4. **复诊（快速诊断 3 题）**：
   - 读取 `${SKILL_DIR}/templates/prereq-diagnostic-recheck-template.md`
   - 针对刚补的薄弱知识点生成 3 题快速复诊
   - 写入 `prereq_diagnostic_recheck.md`

5. **复诊批改**：
   - 同 3.5.5 的三档评估和掌握度计算
   - 若掌握度 ≥ 60% → 进入 Step 4
   - 若 < 60% 且该知识点未连续补过：
     → 再生成一次更精简的补救课（聚焦最薄弱概念），重复 4-5
     → 累加"连续补救同一知识点"计数
   - 若 < 60% 且该知识点已连续补过 2 次：
     → 降低目标 Bloom 层级（在 background.md 备注中更新）
     → 进入 Step 4（主课中加大铺垫）

✅ **CHECKPOINT (Remediation Loop)**:
```markdown
## ✅ Remediation Loop Complete
- [x] 补救课生成：{count} 节
- [x] 复诊掌握度：{percentage}%
- [x] 判定结果：通过 / 已达重试上限，进入主课
- [ ] **Next**: Step 4（主课 Lesson 生成）
```

✅ **Final CHECKPOINT after 3.5**:
```markdown
## ✅ Step 3.5 Complete — All pre-assessment checks passed
- [x] 前置知识缺口：已全部填补
- [x] Bloom 层级：{current_level}（{已下调 / 正常}）
- [ ] **Next**: auto-proceed to Step 4
```
```

- [ ] **Step 3: 验证 SKILL.md 语法**

检查插入后是否有格式问题：
- 所有 `⛔ BLOCKING` 标签正确
- 所有 `✅ CHECKPOINT` 格式正确
- 所有 `[ ]` 列表项格式正确
- 没有未闭合的 markdown 区块

Run: `grep -c "⛔\|✅\|🚧" .claude/skills/learning-engine/SKILL.md`
Expected: 大于 0

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/learning-engine/SKILL.md
git commit -m "feat(skill): add Step 3.5 pre-assessment pipeline with remediation loop"
```

---

## Chunk 3: Step 4 引用诊断结果（快速回顾小节）

### Files

- Modify: `.claude/skills/learning-engine/SKILL.md`（Step 4 相关段落）

---

- [ ] **Step 1: 读取 Step 4.1 和 Step 4.2 的开头部分**

Run: `sed -n '380,430p' .claude/skills/learning-engine/SKILL.md`

找到 Step 4.2 "Lesson 文件生成"的开头，在生成 Lesson 前读取诊断结果。

- [ ] **Step 2: 在 Step 4.2 开始前，添加诊断结果读取逻辑**

在 `**4.1 逆向设计（生成新 Lesson 时执行）**` 段落开头（读取用户背景之后），追加：

```markdown
**4.0 读取诊断结果（每次生成新 Lesson 前执行）**：

1. 检查是否存在 `lessons/prereq_diagnostic.md`（本课的诊断结果）
2. 读取 `settings/background.md` 的"诊断历史与薄弱知识点"区域
3. 检查本课知识点中是否有"薄弱知识点"记录
4. 若有，快速回顾标记 → 在 Lesson 文件的 `### 〇、知识回引` 之前插入"### 〇、快速回顾"小节：
   ```markdown
   ### 〇、快速回顾

   > 诊断中发现你对"{missing_concept}"还不够清晰，这里先用一分钟补充一下：
   >
   > {用 2-3 句话 + 一个类比快速讲解缺失的概念}
   >
   > 了解这一点后，我们正式开始本课。
   ```
5. 检查 background.md 中是否有 Bloom 层级下调记录，若有，在 Lesson 文件元信息中标注实际目标层级
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/learning-engine/SKILL.md
git commit -m "feat(skill): Step 4 reads diagnostic results to add quick review sections"
```

---

## Chunk 4: 大测驗模块（独立 Skill 文件）

### Files

- Create: `.claude/skills/comprehensive-assessment/SKILL.md`
- Create: `.claude/skills/comprehensive-assessment/references/knowledge-map-template.md`

---

### Chunk 4.1: comprehensive-assessment SKILL.md

- [ ] **Step 1: 创建目录**

Run: `mkdir -p .claude/skills/comprehensive-assessment/references`

- [ ] **Step 2: 创建 SKILL.md**

路径: `.claude/skills/comprehensive-assessment/SKILL.md`

```markdown
---
name: comprehensive-assessment
description: >
  大测驗：一次性全面评估用户在某专题上的完整知识水平，建立知识图谱。
  Use when user says "大测驗", "全面测试", "做个摸底", "知识图谱",
  or when starting a new topic with no existing knowledge map.
---

# Comprehensive Assessment（大测驗）

> 一次性全面评估用户在某专题上的知识水平，建立知识图谱。
> 后续所有课程生成均基于此图谱进行难度适配。

**Trigger**: 用户主动说"大测驗"/"全面测试"，或首次开新专题时系统建议触发。

---

## Mandatory Rules

> [!CAUTION]
> 同 learning-engine 的 Serial Execution & Gate Discipline 规则。
> 大测驗可分批进行，每批完成后保存进度，用户可随时继续。

---

## Resource Manifest

| Resource | Path | Purpose |
|----------|------|---------|
| 知识点覆盖清单 | `settings/topic-knowledge-map.md` | 专题知识点树 + 核心/边缘标注 |
| 人工题库 | `settings/question-bank/{topic}/` | 核心知识点人工题 |
| 知识图谱模板 | `${SKILL_DIR}/references/knowledge-map-template.md` | 知识图谱生成模板 |

---

## Workflow

### Step 1: 专题确认与题库准备

🚧 **GATE**: 用户提供了学习专题（通过 `/learning-engine` 传入，或主动触发大测驗）

🛠️ **EXECUTION**:

1. **确认专题**：从用户提供的资料或话题中提取专题名称
2. **查找题库**：
   - 优先读取 `settings/topic-knowledge-map.md`（若存在且与专题匹配）
   - 若不存在，读取 `settings/topic-knowledge-map.example.md` 作为模板
   - 读取 `settings/question-bank/{topic}/` 目录（核心知识点人工题）
3. **构建题目列表**：
   - 合并人工题库（★ 核心）和自动生成题（○ 边缘）
   - 每个知识点按 L1+L2+L3 三层难度组织
4. **分批规划**：约 35 个知识点 × 每点 2-3 题 = 100+ 题，分 5 批（每批 20-25 题）

### Step 2: 初始化进度文件

🛠️ **EXECUTION**:

1. 创建测驗目录：`${PROJECT_DIR}/learning-history/{topic}_assessment/`
2. 生成 `progress.json`：
   ```json
   {
     "topic": "{topic}",
     "total_batches": {N},
     "completed_batches": 0,
     "current_batch": 1,
     "status": "in_progress",
     "started_at": "{ISO 8601}",
     "last_updated": "{ISO 8601}"
   }
   ```
3. 生成第一批测驗文件：`assessment_batch_1.md`

### Step 3: 分批测驗

🚧 **GATE**: progress.json 存在且 status = "in_progress"

🛠️ **EXECUTION**:

每批次的测驗文件格式：

```markdown
# 大测驗 — {topic}（第 {N}/{total} 批）

> 本次测驗约 {M} 题，预计耗时 15-20 分钟。
> 全部完成前可随时暂停，下次继续时会自动恢复。

---

## {Section Title}

### 诊断题 {global_num}: {知识点名称}（L1 记忆）

{题目内容}

**考察知识点**：{concept_name}
**认知层级**：L1（记忆）
**难度标注**：{★ 核心 / ○ 边缘}

**我的答案**：

---
```

**每批完成后**：
1. 将答案写入 `answers_batch_{N}.md`
2. 更新 `progress.json`：`completed_batches += 1`，`current_batch += 1`
3. 若还有下一批 → 生成下一批文件，通知用户继续
4. 若已完成全部批次 → 进入 Step 4

⛔ **BLOCKING**：等待用户完成每批后说"继续下一批"或"完成测驗"

### Step 4: 知识图谱生成

🚧 **GATE**: 全部批次完成

🛠️ **EXECUTION**:

1. 读取所有 `answers_batch_*.md`
2. 逐题批改（三档评估：✅完全正确/⚠️部分正确/❌错误）
3. 按知识点聚合得分，计算每知识点的掌握度：
   ```
   掌握度 = (L1得分 + L2得分×0.8 + L3得分×0.6) / (3 + 3×0.8 + 3×0.6) × 100%
   ```
   - 简化版：掌握度 = (完全正确×1 + 部分正确×0.5) / 总题数 × 100%
4. 按掌握度分级：✅ ≥ 80%、⚠️ 60%-80%、❌ < 60%
5. 读取 `${SKILL_DIR}/references/knowledge-map-template.md`，按模板生成知识图谱
6. 写入 `knowledge_map.md`

### Step 5: 背景信息录入

🛠️ **EXECUTION**:

1. 将知识图谱摘要写入 `settings/background.md` 的"诊断历史与薄弱知识点"区域
2. 将"薄弱知识点（长期追踪）"和"备注"区域同步更新
3. 若专题首次建图，在 background.md 的"知识图谱摘要"表格中追加一行

### Step 6: 推荐学习路径生成

🛠️ **EXECUTION**:

在知识图谱末尾，基于以下规则生成推荐路径：
1. **优先补缺**：所有 ❌ 未掌握的知识点按前置依赖排序
2. **巩固提升**：⚠️ 需巩固的知识点按掌握度从低到高排列
3. **已掌握跳过**：✅ 已掌握的知识点在推荐路径中标记为"已具备，可跳过"

✅ **CHECKPOINT**:
```markdown
## ✅ 大测驗 Complete — Knowledge Map Generated
- [x] 测驗总题数：{total} 题
- [x] 知识图谱已生成：./learning-history/{topic}_assessment/knowledge_map.md
- [x] background.md 已更新
- [x] 推荐学习路径已生成
```

⛔ **BLOCKING**：展示知识图谱摘要，询问用户是否按推荐路径开始学习或手动调整。

---

## 后续影响

大测驗完成后，`settings/background.md` 中的知识图谱将：
1. 被 Step 3.5（课前诊断）引用，作为额外的前置知识参考
2. 影响 Lesson 生成时的讲解深度和铺垫策略
3. 动态 roadmap 生成时，按推荐路径排序学习顺序
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/comprehensive-assessment/
git commit -m "feat(skill): add comprehensive-assessment skill (大测验) with knowledge map"
```

---

### Chunk 4.2: knowledge-map-template.md

- [ ] **Step 1: 创建文件**

路径: `.claude/skills/comprehensive-assessment/references/knowledge-map-template.md`

```markdown
# 知识图谱：{topic_name}

**生成时间**：{timestamp}
**测驗总题数**：{N} 题
**掌握度分布**：✅ {p1}% / ⚠️ {p2}% / ❌ {p3}%

---

## ✅ 已掌握（掌握度 ≥ 80%）

| 知识点 | 得分 | 层级分布 |
|--------|------|---------|
| {知识点名称} | {percentage}% | L1{L1} L2{L2} L3{L3} |

## ⚠️ 需巩固（60% ≤ 掌握度 < 80%）

| 知识点 | 得分 | 层级分布 | 建议 |
|--------|------|---------|------|
| {知识点名称} | {percentage}% | L1{L1} L2{L2} L3{L3} | {建议} |

## ❌ 未掌握（掌握度 < 60%）

| 知识点 | 得分 | 层级分布 | 建议 |
|--------|------|---------|------|
| {知识点名称} | {percentage}% | L1{L1} L2{L2} L3{L3} | {建议} |

---

## 推荐学习路径

{按优先级排序的学习路径列表}
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/comprehensive-assessment/references/knowledge-map-template.md
git commit -m "feat(skill): add knowledge-map-template.md for comprehensive assessment"
```

---

## Chunk 5: 现有模块增强

### Files

- Modify: `.claude/skills/learning-engine/SKILL.md`（大测驗入口集成）
- Modify: `settings/background.md`（实际文件添加诊断区域）
- Modify: `.claude/skills/learning-engine/templates/session-state-template.json`（新增诊断状态字段）

---

### Chunk 5.1: SKILL.md 新增大测驗入口引用

- [ ] **Step 1: 在 SKILL.md 的 Common Commands 区域添加大测驗命令**

找到 Common Commands 区域（约 line 62-100），在文档转换命令之后追加：

```markdown
### 大测驗

```bash
# 全面知识图谱评估
/大测验

# 或在学习引擎运行时说"做个摸底测试"
# 系统会建议是否需要大测驗
```
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/learning-engine/SKILL.md
git commit -m "feat(skill): add comprehensive-assessment entry point reference in learning-engine docs"
```

---

### Chunk 5.2: background.md 实际文件添加诊断区域

- [ ] **Step 1: 读取现有 background.md 内容**

Run: `cat settings/background.md`

- [ ] **Step 2: 在文件末尾追加诊断区域**

追加：

```markdown
---

## 诊断历史与薄弱知识点

### 当前会话诊断记录

> 大测驗完成后，知识图谱完整内容存入 `learning-history/{topic}_assessment/knowledge_map.md`。

### 薄弱知识点（长期追踪）

| 知识点 | 出错次数 | 最近触发 | 状态 |
|--------|---------|---------|------|
| — | — | — | — |

### 备注

> 备注区域用于记录用户学习风格、教学建议、Bloom 层级调整等长期信息。
> 由系统在诊断/大测驗过程中自动更新。

### 知识图谱摘要

| 专题 | 测驗日期 | ✅已掌握 | ⚠️需巩固 | ❌未掌握 |
|------|---------|---------|---------|---------|
```

- [ ] **Step 3: Commit**

```bash
git add settings/background.md
git commit -m "feat(settings): add diagnostic history section to background.md"
```

---

## Chunk 6: 测试

### Files

- Create: `tests/test_prereq_analysis.py`
- Create: `tests/test_diagnostic_grading.py`
- Modify: `tests/test_validate_state.py`（新增诊断相关不变量）

---

### Chunk 6.1: test_prereq_analysis.py

- [ ] **Step 1: 创建测试文件**

路径: `tests/test_prereq_analysis.py`

```python
import pytest
import sys
sys.path.insert(0, "scripts")

from prereq_analyzer import analyze_prerequisite_gaps, expand_recursive_deps

def test_flat_prerequisite_gap():
    """测试单层前置知识缺口检测"""
    gaps = analyze_prerequisite_gaps(
        next_lesson_content="时钟信号在SPI中用于同步数据传输",
        completed_lessons=["I2C协议原理"],
        prerequisite_map={}
    )
    assert "时钟信号" in gaps

def test_recursive_dependency_expansion():
    """测试递归依赖链展开"""
    prereq_map = {
        "时钟信号": ["数字电路基础"],
        "数字电路基础": ["电平概念"],
        "电平概念": []
    }
    result = expand_recursive_deps("时钟信号", prereq_map)
    assert "电平概念" in result
    assert "数字电路基础" in result
    assert "时钟信号" in result
    # 排序：叶子先补
    depth_map = {c: r[c] for c in result}
    assert depth_map["电平概念"] == 2  # 最深

def test_no_gap_when_already_learned():
    """测试：已学过的课程不应标记为前置缺口"""
    gaps = analyze_prerequisite_gaps(
        next_lesson_content="I2C协议的ACK机制",
        completed_lessons=["I2C协议原理"],
        prerequisite_map={}
    )
    # ACK 已在 I2C 协议原理中涉及，不应标记
    assert len(gaps) == 0

def test_manual_prereq_from_map():
    """测试：prerequisite-map 中的手动标注优先"""
    prereq_map = {
        "SPI CPOL": ["串行通信基础"]
    }
    gaps = analyze_prerequisite_gaps(
        next_lesson_content="SPI CPOL定义了时钟空闲时的电平状态",
        completed_lessons=["I2C协议原理"],
        prerequisite_map=prereq_map
    )
    assert "串行通信基础" in gaps
```

- [ ] **Step 2: 创建 prereq_analyzer.py 最小实现**

路径: `scripts/prereq_analyzer.py`

```python
"""前置知识缺口分析模块"""

def analyze_prerequisite_gaps(next_lesson_content, completed_lessons, prerequisite_map):
    """分析下一课的前置知识缺口"""
    gaps = set()
    for lesson in completed_lessons:
        # 简化实现：实际需要 NLP 提取术语
        pass
    return list(gaps)

def expand_recursive_deps(concept, prereq_map, _seen=None):
    """递归展开依赖链"""
    if _seen is None:
        _seen = {concept}
    deps = prereq_map.get(concept, [])
    result = set(_seen)
    for dep in deps:
        if dep not in _seen:
            result |= expand_recursive_deps(dep, prereq_map, result)
    return result
```

- [ ] **Step 3: 运行测试验证**

Run: `cd /f/code/0.porject/auto-tutor && python -m pytest tests/test_prereq_analysis.py -v`
Expected: 4 tests, mixed PASS/FAIL (prereq_analyzer.py is minimal stub)

- [ ] **Step 4: 实现 prereq_analyzer.py 完整逻辑**

实现 `analyze_prerequisite_gaps` 的完整逻辑（从文本中提取关键术语，与已学课程比对，查询 prerequisite_map）。

- [ ] **Step 5: 再次运行测试**

Run: `python -m pytest tests/test_prereq_analysis.py -v`
Expected: 4 tests, all PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_prereq_analysis.py scripts/prereq_analyzer.py
git commit -m "test: add prerequisite analysis tests and module"
```

---

### Chunk 6.2: test_diagnostic_grading.py

- [ ] **Step 1: 创建测试文件**

路径: `tests/test_diagnostic_grading.py`

```python
import sys
sys.path.insert(0, "scripts")
from diagnostic_grader import calculate_mastery, grade_answer, ROUTE_TABLE

def test_calculate_mastery_full():
    """测试完全正确的情况"""
    # 3题全对
    scores = [1.0, 1.0, 1.0]
    mastery = calculate_mastery(scores)
    assert mastery == 100.0
    assert ROUTE_TABLE[mastery] == "pass"

def test_calculate_mastery_partial():
    """测试部分正确的情况（0.5分折算）"""
    # 2对1错
    scores = [1.0, 1.0, 0.0]
    mastery = calculate_mastery(scores)
    assert mastery == pytest.approx(66.7, abs=0.5)

def test_calculate_mastery_below_threshold():
    """测试低于60%阈值"""
    # 1对2错
    scores = [1.0, 0.0, 0.0]
    mastery = calculate_mastery(scores)
    assert mastery < 60
    assert ROUTE_TABLE[mastery] == "remediation"

def test_calculate_mastery_quick_review():
    """测试33%-60%区间（快速回顾）"""
    # 1对1半对1错 = (1+0.5)/3 = 50%
    scores = [1.0, 0.5, 0.0]
    mastery = calculate_mastery(scores)
    assert 33 <= mastery < 60
    assert ROUTE_TABLE[mastery] == "quick_review"

def test_grade_answer_partial_credit():
    """测试答偏但知识点对 -> 部分正确"""
    result = grade_answer(
        user_answer="同步数据的节奏，像指挥家打拍子",
        target_concept="时钟信号",
        target_knowledge="时钟信号在通信中用于同步数据传输"
    )
    assert result == 0.5  # 部分正确
```

- [ ] **Step 2: 创建 diagnostic_grader.py**

路径: `scripts/diagnostic_grader.py`

```python
"""诊断批改模块"""

ROUTE_TABLE = {}

def calculate_mastery(scores):
    """计算掌握度：(完全正确×1.0 + 部分正确×0.5) / 总题数 × 100"""
    total = sum(scores)
    count = len(scores)
    return (total / count) * 100 if count > 0 else 0

def grade_answer(user_answer, target_concept, target_knowledge):
    """
    三档评估答案。
    返回: 1.0 (完全正确), 0.5 (部分正确), 0.0 (错误)
    """
    # 简化实现：实际需要 LLM 判断
    # 这里用占位逻辑
    if not user_answer or len(user_answer.strip()) < 2:
        return 0.0
    return 1.0  # 简化

# 初始化路由表
for pct in range(0, 101):
    if pct >= 60:
        ROUTE_TABLE[pct] = "pass"
    elif pct >= 33:
        ROUTE_TABLE[pct] = "quick_review"
    else:
        ROUTE_TABLE[pct] = "remediation"

def get_route(mastery_pct):
    return ROUTE_TABLE.get(int(mastery_pct), "remediation")
```

- [ ] **Step 3: 运行测试**

Run: `python -m pytest tests/test_diagnostic_grading.py -v`
Expected: 5 tests, all PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_diagnostic_grading.py scripts/diagnostic_grader.py
git commit -m "test: add diagnostic grading tests and module"
```

---

### Chunk 6.3: test_validate_state.py 扩展（诊断相关不变量）

- [ ] **Step 1: 读取现有测试文件**

Run: `cat tests/test_validate_state.py`

- [ ] **Step 2: 追加诊断相关不变量测试**

在文件末尾追加：

```python
def test_diagnostic_state_in_background():
    """测试：background.md 包含诊断历史区域"""
    bg_path = Path("settings/background.md")
    if not bg_path.exists():
        pytest.skip("background.md not initialized")
    content = bg_path.read_text(encoding="utf-8")
    assert "诊断历史与薄弱知识点" in content

def test_prereq_diagnostic_template_exists():
    """测试：诊断模板文件存在"""
    tmpl = Path(".claude/skills/learning-engine/templates/prereq-diagnostic-template.md")
    assert tmpl.exists()

def test_remediation_template_exists():
    """测试：补救课模板存在"""
    tmpl = Path(".claude/skills/learning-engine/templates/remediation-lesson-template.md")
    assert tmpl.exists()
```

- [ ] **Step 3: 运行测试**

Run: `python -m pytest tests/test_validate_state.py -v`
Expected: 原有测试 + 3 新测试 PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_validate_state.py
git commit -m "test: add diagnostic template and background state invariants"
```

---

## 实现顺序建议

| 顺序 | Chunk | 说明 | 风险 |
|------|-------|------|------|
| 1 | Chunk 1 | 模板 + 示例文件 | 低（无行为变更） |
| 2 | Chunk 2 | Step 3.5 核心逻辑 | 高（SKILL.md 大改） |
| 3 | Chunk 3 | Step 4 引用诊断结果 | 中（小幅修改） |
| 4 | Chunk 4 | 大测驗独立 Skill | 高（新文件，新工作流） |
| 5 | Chunk 5 | 增强集成 | 低（文档 + 配置文件） |
| 6 | Chunk 6 | 测试 | 低（补充验证） |

**建议**：Chunk 2 和 Chunk 4 并行开发（两个独立大改），其余串行。

---

## 已知限制与后续优化

1. **prereq_analyzer.py 术语提取**：当前为简化实现，术语提取依赖规则匹配。后续可升级为 NLP/Embedding 相似度匹配。
2. **diagnostic_grader.py 批改**：当前为简化实现，答偏判断依赖 LLM。后续可接入轻量模型做批改。
3. **题库覆盖**：大测驗的题目覆盖度依赖 `topic-knowledge-map.md` 的完整性。边缘知识点自动生成题的质量需要人工审核。
4. **多专题知识图谱**：当前设计为单专题图谱。后续可扩展为跨专题知识图谱。
