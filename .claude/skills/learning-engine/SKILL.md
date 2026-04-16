---
name: learning-engine
description: >
  交互式学习引擎，采用苏格拉底教学法和布卢姆分类学引导用户深入学习。
  Use when user says "学习引擎", "帮我学习这个文档", invokes /learning-engine,
  or provides a learning material and asks to study it.
---

# Learning Engine（学习引擎）

> 以"文件驱动 + 苏格拉底教学法 + 布卢姆分类学"为核心，引导用户对学习资料实现深度知识内化的交互式学习引擎。

**Core Pipeline**: `文件预处理 → 初始化与历史检索 → 上下文恢复 → 文件驱动交互式学习 → 学习报告`

---

## Mandatory Rules

> [!CAUTION]
> ### Serial Execution & Gate Discipline
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST execute in order; output of each step is input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **BLOCKING = HARD STOP** — ⛔ BLOCKING steps require full stop; agent MUST wait for explicit user response before proceeding and MUST NOT make decisions on behalf of the user
> 3. **NO CROSS-PHASE BUNDLING** — Bundling work across phases is FORBIDDEN
> 4. **GATE BEFORE ENTRY** — Prerequisites (🚧 GATE) MUST be verified before starting each Step
> 5. **NO SPECULATIVE EXECUTION** — Pre-preparing content for future steps is FORBIDDEN

> [!IMPORTANT]
> ### Language & Communication
>
> - Match the language of the user's input. If the user writes in Chinese, respond in Chinese; if in English, respond in English
> - Explicit user override takes precedence
> - Lesson 文件内容使用中文；文件结构关键词（如 `## 学习目标`、`## 课后习题`、`**我的答案**`）保持固定格式，不得更改
>
> **跨语言教学（强制执行）**：
>
> 若用户指定的教学语言与学习材料的语言不同（例如：材料为中文，但要求英文教学），则：
>
> 1. **翻译前置**：在生成 Lesson 内容前，先读取 `${PROJECT_DIR}/settings/glossary.md` 中的术语表
> 2. **术语优先**：翻译时，所有出现在术语表中的专有名词必须严格使用术语表中对应的译法，不得自行翻译
> 3. **全文翻译**：Lesson 文件的所有正文内容（讲解、习题、反馈）均使用目标教学语言输出；文件结构关键词（如 `## 学习目标`、`**我的答案**`）保持固定格式不变
> 4. **术语标注**：首次出现的专有名词，在译文后以括号附注原文，格式：`Derivative（导数）`
> 5. **术语表缺失处理**：若某专有名词未收录于术语表，使用通行译法并在该词后标注 `[⚠️ 术语表未收录]`

> [!IMPORTANT]
> ### Compatibility With Generic Coding Skills
>
> - Do NOT create `.worktrees/`, `tests/`, branch workflows, or other generic engineering structure
> - If generic coding skills conflict with this workflow, follow this skill first unless the user explicitly overrides

> [!IMPORTANT]
> ### 防幻觉（强制执行）
>
> - ❌ 禁止编造数据、虚构事件、臆测因果关系
> - ✅ 讲解中涉及资料内容时，必须使用 `> **资料原文**：` 格式标注原文
> - ✅ 资料未覆盖的知识点，必须明确告知用户"当前资料未涉及此内容"

> [!IMPORTANT]
> ### 用户背景适配（强制执行）
>
> 生成的课程内容必须符合【用户背景】：
> - 用户背景来源：
>   1. `${PROJECT_DIR}/settings/background.md` 中的背景信息
>   2. 用户在调用 skill 时补充的背景信息
> - 优先级：用户补充的背景信息 > `background.md` 中的背景信息
> - 若两者存在冲突，以用户补充为准
> - 适配要求：
>   - 讲解深度、用词、举例应适配用户的年级/知识水平
>   - 习题难度应与用户能力匹配
>   - 若用户背景表明其是教师（如家教），讲解可包含教学策略建议

> [!IMPORTANT]
> ### 文件驱动核心原则（强制执行）
>
> | 禁止行为 | 原因 |
> |---------|------|
> | ❌ 在对话中展示课程讲解内容 | 违反文件驱动原则 |
> | ❌ 在对话中展示课后习题 | 用户应在文件中阅读习题 |
> | ❌ 让用户在对话中发送答案 | 用户应在文件中填写答案 |
> | ❌ 在对话中直接检查答案 | 必须先读取文件中的答案 |
>
> **唯一允许的对话内容**：通知文件位置、提醒填写答案、读取文件后给出反馈、补充讲解。
>
> **例外**：Step 3 的快速复习测试为轻量遗忘检测，不属于正式课程，允许在对话中进行问答。

> [!IMPORTANT]
> ### 状态管理原则（强制执行）
>
> | 层级 | 文件 | 定位 | 写入时机 |
> |------|------|------|---------|
> | **权威源** | `session_state.json` | 机器可读的唯一状态源 | 每次状态变更时**首先**写入 |
> | 派生视图 | `summary.md` | 人类可读摘要 | 从 `session_state.json` + `lessons/` 派生，允许追加笔记 |
> | 派生视图 | `roadmap_status.md` | 人类可读进度 | 从 `session_state.json` 的进度字段派生 |
> | 派生视图 | `_ai_context.md` | AI 断点恢复上下文 | 从 `session_state.json` + 学习历史派生 |
>
> **规则**：当 `session_state.json` 与 Markdown 视图不一致时，以 `session_state.json` 为准。
> 派生视图可包含 `session_state.json` 中不存在的补充信息（如详细笔记、教学决策日志），但核心进度字段必须与权威源保持一致。

### Role Dispatch Protocol

This skill operates as a single inline agent — no role switching required.

---

## Resource Manifest

### Templates

| Index | Path | Purpose |
|-------|------|---------|
| Lesson 模板 | `${SKILL_DIR}/templates/lesson-template.md` | 每节课的内容结构模板 |
| 摘要模板 | `${SKILL_DIR}/templates/summary-template.md` | `summary.md` 初始化模板 |
| 路线图模板 | `${SKILL_DIR}/templates/roadmap-template.md` | `roadmap_status.md` 初始化模板 |
| 报告模板 | `${SKILL_DIR}/templates/report-template.md` | 学习报告结构模板 |
| 状态模板 | `${SKILL_DIR}/templates/session-state-template.json` | `session_state.json` 初始化模板（v2.1，含 learner_model） |
| 状态 Schema | `${SKILL_DIR}/templates/session-state.schema.json` | `session_state.json` 字段校验 Schema |
| 项目概览模板 | `${SKILL_DIR}/templates/project-overview-template.md` | 开源项目学习资料生成模板 |
| 复习队列模板 | `${SKILL_DIR}/templates/review-queue-template.json` | 错题复习队列初始化模板 |
| 架构图模板 | `${SKILL_DIR}/templates/architecture-map-template.md` | GitHub 项目学习可选产物：模块依赖与数据流 |
| 阅读顺序模板 | `${SKILL_DIR}/templates/file-reading-order-template.md` | GitHub 项目学习可选产物：源码阅读路径与首次贡献建议 |
| 指标模板 | `${SKILL_DIR}/templates/metrics-template.json` | 会话事件日志，用于教学策略量化分析 |
| 诊断模板 | `${SKILL_DIR}/templates/prereq-diagnostic-template.md` | 课前诊断文件生成模板 |
| 复诊模板 | `${SKILL_DIR}/templates/prereq-diagnostic-recheck-template.md` | 补救课后复诊文件模板 |
| 补救课模板 | `${SKILL_DIR}/templates/remediation-lesson-template.md` | 前置补救课内容模板 |

| Resource | Path |
|----------|------|
| 布卢姆分类学 | `${SKILL_DIR}/references/bloom-taxonomy.md` |
| 苏格拉底教学法 | `${SKILL_DIR}/references/socratic-method.md` |

### User Context

| Resource | Path | Purpose |
|----------|------|---------|
| 用户背景 | `${PROJECT_DIR}/settings/background.md` | 学习者的年级、科目、问题等背景信息 |

---

## Common Commands

### 大测驗

```bash
# 全面知识图谱评估（一次性摸底某专题的完整知识水平）
/大测验

# 或在学习引擎运行时说"做个摸底测试"
# 系统会建议是否需要大测驗
```

---

## Workflow

### Step 1: 文件格式预处理 (File Format Preprocessing)

🚧 **GATE**: 用户已提供学习资料——文件路径、目录路径、GitHub 链接或内容。

🛠️ **EXECUTION**:

1. **输入类型判断**：

| 输入形式 | 判断条件 | 处理方式 |
|---------|---------|---------|
| GitHub 链接 | 以 `https://github.com/` 开头 | 执行第 2 步（项目获取） |
| 本地目录路径 | 路径指向一个目录 | 执行第 2 步（项目获取） |
| 单个文件 | 路径指向一个文件 | 执行第 3 步（格式检测） |
| 不可读文件类型 | 见下方不可读类型列表 | 执行第 6 步（报错终止） |

**不可读文件类型**（报错终止）：`.exe` / `.dll` / `.so` / `.bin` / `.dat` / `.zip` / `.tar` / `.gz` 等二进制或压缩格式。

2. **开源项目获取与学习资料生成**：

   **若为 GitHub 链接**：
   ```bash
   git clone {github_url} ${PROJECT_DIR}/tmp/{repo_name}/
   ```
   - 失败则重试，最多 3 次；超过 3 次提示用户检查链接或网络

   **若为本地目录路径**：
   将本地目录复制到项目临时目录（根据操作系统选择命令）：
   - **macOS / Linux**：`cp -r {local_path} ${PROJECT_DIR}/tmp/{project_name}/`
   - **Windows**：`xcopy /E /I "{local_path}" "${PROJECT_DIR}\tmp\{project_name}\"`

   **项目读取与学习资料生成**：
   - 读取项目根目录下的 `README.md`（若存在）作为概览
   - 扫描项目文件树，识别主要模块与入口文件
   - 读取 `${SKILL_DIR}/templates/project-overview-template.md`
   - 启动 subagent（`general-purpose` 类型），按模板生成结构化学习资料：
     ```
     请分析以下开源项目，严格按照提供的模板生成学习概览文件。

     项目路径：{project_path}
     输出文件：${PROJECT_DIR}/tmp/converted/{project_name}_overview.md
     模板路径：${SKILL_DIR}/templates/project-overview-template.md

     生成要求：
     1. 按模板的 8 个章节逐一填写，不得省略任何章节
     2. 所有内容必须有来源依据（README、代码文件、注释）；无法确认来源的内容标注 [⚠️ 当前资料未涉及此内容]
     3. 第 3 节"项目结构"：用 tree 格式展示两级目录，超过 20 个条目时折叠次要目录
     4. 第 4 节"核心模块"：每个模块必须标注入口文件的实际路径
     5. 第 5 节"数据流"：必须追踪至少一条从入口到输出的完整调用链
     6. 第 7 节"推荐学习路径"：按模块依赖关系排序，每条对应后续一个 Lesson 的学习单元
     7. 不得编造函数名、类名、文件路径——所有符号必须在项目中实际存在
     ```
   - 轮询检查 subagent 状态（poll_interval = 10s，最大等待 300s）
   - 失败则重试，最多 3 次；超过 3 次提示用户手动提供学习资料
   - 将生成的 `_overview.md` 作为后续步骤的 `processed_path`，跳至第 5 步

3. **格式检测**：判断文件后缀：

| 类型 | 文件格式 | 处理方式 |
|------|---------|---------|
| 直接可读（无需转换） | `.md` 及各类源码（`.c` `.cpp` `.py` `.java` `.js` `.ts` `.go` `.rs` `.rb` `.swift` `.kt` 等） | 跳至第 4 步 |
| 需转换为 Markdown | `.pdf` `.docx` `.pptx` `.png` `.jpg` `.html` 等 | 执行第 4 步前先执行转换 |

> ⚠️ `.html` 默认需要转换，除非用户明确表示学习目标是"学习如何书写 HTML"。

4. **非直接可读文件转换**：
   - 启动 subagent（`general-purpose` 类型），调用 `everything-to-markdown` skill 进行格式转换
   - 输出目录：`${PROJECT_DIR}/tmp/converted/`
   - 使用以下 prompt 模板：
     ```
     请调用 everything-to-markdown skill，将以下文件转换为 Markdown 格式：
     - 输入文件：{file_path}
     - 输出目录：./tmp/converted/
     转换完成后，返回输出文件的完整路径。
     ```
   - 轮询检查 subagent 状态（poll_interval = 10s，最大等待 300s）
   - 失败则重试，最多 3 次；超过 3 次提示用户手动转换

5. **Markdown 质量检测与优化**：
   - 读取文件前 500 行，检测：标题层级错乱、OCR 噪声、格式不规范
   - 若存在问题：启动 subagent 调用 `markdown-refiner` skill，**按章节分段传递**（不传整个文件）
   - 使用以下 prompt 模板：
     ```
     请调用 markdown-refiner skill，优化以下 Markdown 文本片段。
     这是学习资料的一个章节，请修复标题层级、OCR 错误和格式问题。
     【待优化内容】
     {chapter_content}
     仅输出优化后的 Markdown 文本，不要添加解释说明。
     ```
   - 轮询与重试机制同上

6. **不可读文件类型报错（终止）**：
   ```
   ❌ 无法处理该文件类型：{file_extension}
   当前支持的格式：Markdown、源码文件、PDF、Word、PPT、图片、HTML，以及 GitHub 链接或本地项目目录。
   请提供可读的学习资料后重新调用。
   ```
   终止 workflow，不进入 Step 2。

7. **记录文件状态**：
   - `original_path`：原始文件路径或链接
   - `processed_path`：处理后文件路径
   - `processing_status`：`original` | `cloned` | `converted` | `refined`

✅ **Step 1 完成**：输入类型判断完成，文件已就绪（路径：`{processed_path}`，状态：`{processing_status}`）。

→ **直接进入 Step 2**

---

### Step 2: 初始化与历史检索 (Initialization & History Retrieval)

🚧 **GATE**: Step 1 complete；`processed_path` 已确认，文件可读。

🛠️ **EXECUTION**:

1. **主题提取**：根据资料内容自动提炼 `topic_slug`——全小写 ASCII、单词以连字符分隔（如 `quantum-physics`、`python-async`）。中文主题使用英文翻译或拼音
2. **获取时间戳**：记录 `timestamp`（固定格式：`YYYY-MM-DD-HH-MM`，不可省略时分）
3. **扫描历史**：检索 `${PROJECT_DIR}/learning-history/` 下所有子目录
4. **智能筛选**：根据文件夹名（格式 `${topic_name}_${timestamp}`）筛选相关历史
5. **深度核实**：读取相关目录下的 `summary.md`，确认学习进度与目标一致性
6. **构建选项列表**：
   - 每条历史记录：`[文件夹名] - 上次学习到：[summary.md 中的进度摘要]`
   - 末尾追加：`开启全新学习`

**历史选择路由规则**（三段式）：

| 历史记录数 | 行为 | 说明 |
|-----------|------|------|
| **0 条** | 直接创建新会话 | 无需询问，直接执行 Step 3 的新会话初始化 |
| **1 条** | 自动选择该记录，输出通知 | `"✅ 检测到 1 条历史记录，自动继续：[历史名]"`，然后执行 Step 3 |
| **2+ 条** | ⛔ **BLOCKING**：`ask_user_question` 询问选择 | 用户选择后执行 Step 3 |

✅ **Step 2 完成**：topic_name = `{topic_name}`，timestamp = `{timestamp}`，历史选择路由已确定（{选择结果}）。

→ **直接进入 Step 3**

---

### Step 3: 上下文恢复 (Context Recovery)（Conditional）

🚧 **GATE**: Step 2 complete；用户已做出选择。

> **Trigger condition**: 用户选择了继续某条历史记录。若用户选择"开启全新学习"，则创建新目录并初始化文件后，跳至 Step 4。

🛠️ **EXECUTION**:

**若用户选择全新学习**：
1. 创建目录 `${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/lessons/`
2. 读取 `${SKILL_DIR}/templates/summary-template.md`，初始化 `summary.md`
3. 读取 `${SKILL_DIR}/templates/roadmap-template.md`，初始化 `roadmap_status.md`
4. 读取 `${SKILL_DIR}/templates/ai-context-template.md`，初始化 `_ai_context.md`，填入：资料来源路径、转换后路径、用户背景水平初始判断
5. 读取 `${SKILL_DIR}/templates/session-state-template.json`，初始化 `session_state.json`（v2.0），填入：`topic_id`、`source_path`、`processed_path`、`source_hash`（源文件 SHA-256）、`phase` ← `"learning"`、`total_lessons`（来自 roadmap 规划）、`learning_language`、`created_at`、`updated_at`
   - 若学习资料为 GitHub 仓库或本地 Git 目录：记录 `repo_commit_hash` ← 当前 HEAD commit hash（通过 `git rev-parse HEAD` 获取）
6. 跳至 Step 4

**若用户选择继续历史**：
1. **优先读取 `session_state.json`**：获取 `phase`、`current_lesson`、`last_completed_lesson`、`counterfactual_mode`、`wait_reason`、`mastery_rate` 等机器状态（唯一权威源）
2. 读取 `_ai_context.md`：恢复用户画像、错误模式、教学决策日志
3. 读取 `summary.md`：获取核心结论、已掌握知识点、待攻克难点
4. 读取 `roadmap_status.md`：获取知识点追踪详情
5. 读取 `review_queue.json`（若存在）：获取待复习错题列表，优先复习 `status: "pending"` 且 `next_review_at` 已到期的条目
6. **增量学习检测**（仅 GitHub/Git 仓库）：若 `session_state.json` 中 `repo_commit_hash` 非 null，获取当前 HEAD commit hash 并对比——若有变化，提示用户："仓库自上次学习后有 N 个新 commit，是否生成增量课程覆盖变更内容？"用户确认后，对 diff 生成 `delta_overview.md` + `lessons/delta_lesson_{N}.md`
7. **触发式遗忘检测**（若 `review_queue.json` 中有到期复习项则直接使用，否则走下方规则）：
   - 读取 `summary.md` 的 `最后更新` 时间戳，计算距今天数
   - 读取"错题记录"表格中状态为"✅ 已纠正"的条目（即曾犯错但已纠正的知识点——最容易遗忘）
   - 按以下规则决定是否插入复习：

   | 距上次学习天数 | 已纠正错题数 | 操作 |
   |--------------|------------|------|
   | ≤ 3 天 | 任意 | 跳过复习，直接进入新课 |
   | 4-14 天 | ≥ 1 | 插入快速复习：从已纠正错题中抽取 2-3 道，生成简化版复习测试（仅习题 + 答案区，无讲解），用户完成后再进入新课 |
   | 4-14 天 | 0 | 跳过复习（无历史错题可复习） |
   | > 14 天 | ≥ 1 | 插入复习 + 在对话中提醒："距上次学习已超过两周，建议先回顾前几课的要点总结再继续" |
   | > 14 天 | 0 | 在对话中提醒间隔较长，建议用户自行翻阅之前的 lesson 文件回顾 |

   > **复习测试不生成独立 lesson 文件**，直接在对话中以代码块形式呈现，用户在对话中回答即可。答对 → 确认记忆保持；答错 → 更新错题记录表中该条目状态为"❌ 未纠正"，并在下一课讲解中穿插相关概念的回顾。

4. 检查当前 lesson 文件状态，按下表路由：

| 场景 | lesson 文件状态 | 用户答案状态 | 正确行为 |
|------|----------------|-------------|---------|
| A | 不存在 | — | 跳至 Step 4，生成新 lesson |
| B | 已存在 | "我的答案"区域为空 | ⛔ BLOCKING：通知用户去文件中填写，等待"已完成" |
| C | 已存在 | "我的答案"区域已填写 | 跳至 Step 4，执行答案检查 |

**场景 B 通知模板**：
```
📋 检测到 Lesson {index} 已生成，但尚未完成。

📄 文件位置：`./learning-history/${topic_name}_${timestamp}/lessons/lesson_{index}.md`

请阅读该文件，在"我的答案"区域填写你的答案，保存文件后，在对话窗口告诉我"已完成"。
```

✅ **Step 3 完成**：学习目录已就绪，summary.md/roadmap_status.md 已加载，当前 lesson 状态：场景 {A/B/C}。

→ **直接进入 Step 4**

---

### Step 3.5: 课前诊断（Pre-Assessment with Confidence-Aware Adaptive Routing）

🚧 **GATE**: Step 3 complete；学习目录存在，当前 lesson index 已确定；用户背景已加载；`session_state.json`（含 `learner_model`）已读取。

> **前置说明**：此步骤在学习新 Lesson 之前检测用户是否具备所需的前置知识，并通过**自信度**识别学习模式（过度自信 vs 谨慎型），为教学策略适配提供数据支撑。
> 诊断结果不仅决定"跳过快进 / 压缩讲解 / 完整学习 / 补救课"的路由，还更新 `session_state.json` 的 `learner_model` 字段。

🛠️ **EXECUTION**:

**3.5.1 前置知识缺口分析（自动 + 手动）**：

1. **递归依赖链展开**：读取 `settings/prerequisite-map.md`（若存在），对下一课涉及的核心概念递归展开依赖链
2. **自动检测**：对下一课草稿中出现的术语，若在已学课程中从未出现，标记为潜在前置缺口
3. **合并去重**：合并自动检测 + prerequisite-map 手动标注的结果
4. **查询学习者模型**：读取 `session_state.json` 的 `learner_model.concept_mastery`，获取相关已测概念的掌握度和自信度偏差，用于精准定位薄弱环节

**3.5.2 诊断模式选择**：

在对话中发送诊断模式选择菜单，快速模式(3题)或完整模式(8题)

**3.5.3 生成诊断小测**：

1. 读取模板 `${SKILL_DIR}/templates/prereq-diagnostic-template.md`，根据前置缺口生成诊断题
2. **每道题必须包含**：
   - 题目内容（绑 `concept_tag`，与 Step 4.1 的 lesson 元信息中的 concept_tags 对应）
   - 难度适中（目标 Bloom 层级 2-3）
   - 与 `session_state.json` 的 `learner_model.bloom_target` 保持一致
3. 诊断题数量：快速模式 3 题，完整模式 8 题；每题覆盖一个独立 concept_tag，避免重叠

**3.5.4 诊断通知**：

通知用户诊断文件位置，特别提醒：
```
> ⚠️ 作答前，请先在"自信度"区选择你对本题的把握程度（1-5 分）。
> 自信度影响教学策略：高自信度 + 答错 → 系统判定为"过度自信"，会提供更多脚手架；
> 低自信度 + 答对 → 系统判定为"谨慎型"，讲解时会更注重直觉类比。
```

⛔ **BLOCKING**：等待用户说"诊断完成"或选择跳过

**3.5.5 批改、自信度分析与路由判定**：

1. 读取诊断文件，提取每道题的：
   - **答案正确性**：`✅` 完全正确 / `⚠️` 部分正确 / `❌` 错误
   - **自信度**：用户作答前选择的 1-5 分
2. **自信度偏移检测**（按 concept_tag 分别计算）：
   - `过度自信`：自信度 ≥ 4 且答案 `❌` 或 `⚠️`
   - `校准良好`：自信度与正确性大致匹配
   - `谨慎型`：自信度 ≤ 2 且答案 `✅`
   - `不确定型`：自信度 ≤ 2 且答案 `❌` 或 `⚠️`
3. **综合掌握度** = (完全正确×1.0 + 部分正确×0.5 + 错误×0.0) / 总题数 × 100%
4. **四档路由判定**：

   | 综合掌握度 | 主导模式 | 路由 |
   |-----------|---------|------|
   | ≥ 80% | 任意 | **Skip** → 直接进入 Step 4，讲解可压缩 |
   | 60-79% | 校准良好 | **Compact** → 快速回顾薄弱点后进入 Step 4 |
   | 60-79% | 过度自信 / 谨慎型 | **Full** → 完整讲解，且增加 Worked Example |
   | 33-59% | 任意 | **Remedial** → 插入前置补救课（每缺口 1 个） |
   | < 33% | 任意 | **Remedial** → 补救课 + 复诊 + Bloom 层级评估 |

5. 对每个 concept_tag，更新 `session_state.json` 的 `learner_model.concept_mastery[concept_tag]`：

   若该 concept_tag 无记录，创建：
   ```json
   "<concept_tag>": {
     "lesson_index": <当前 lesson index>,
     "mastery_level": "<掌握度<33%→weak / 33-59%→developing / ≥60%→strong>",
     "confidence_bias": "<检测到的偏移模式>",
     "misconception_tags": [],
     "test_count": 1,
     "correct_count": <1 若完全正确，否则 0>,
     "last_tested_at": "<ISO 8601>"
   }
   ```

   若该 concept_tag 已有记录，合并更新（test_count/correct_count 累加，mastery_level 取较低值，confidence_bias 取最新检测结果）。
6. 更新 `session_state.json` 的 `learner_model.overall_confidence_bias`：计算所有本轮测过 concept_tag 的 confidence_bias 众数。
7. 更新 `learner_model.last_updated_at` ← 当前 ISO 8601 时间戳。

**3.5.6 Bloom层级动态下调**：

连续 2 次补救课后，读取 `session_state.json` 的 `learner_model.bloom_target`，执行下调：
- 新值 ← max(1, 当前值 - 1)
- 将新值写入 `learner_model.bloom_target`
- 在 background.md 的"备注"区追加记录："Bloom 层级调整：L{N-1}（连续补救课触发）"

✅ **CHECKPOINT**:
```markdown
## ✅ Step 3.5 Complete
- [x] 前置知识缺口分析完成
- [x] 诊断完成（{N}题，含自信度）
- [x] learner_model 已更新（{M}个 concept_tag）
- [x] 路由：{Skip/Compact/Full/Remedial}
- [ ] **Next**: auto-proceed based on result
```

**3.5.7 教学策略适配通知**：

路由完成后，在对话中通知路由结果，格式：
```
📊 诊断完成 | 掌握度：{X}% | 主导模式：{模式标签}
🎯 路由：{Skip/Compact/Full/Remedial}
💡 教学建议：{根据模式给出提示}
```

- **Skip**：讲解时间可压缩 50%，直接进入渐进训练
- **Compact**：用 1-2 句话快速回顾薄弱点，再进入完整讲解
- **Full**：完整讲解，且在 Lesson 中额外增加 Worked Example 示范
- **Remedial**：前置补救课完成后，复诊通过方可进入主课

**3.5.7 前置补救课插入 + 闭环**：

触发条件：掌握度<33%

1. 生成前置补救课（每个缺口单独1个）
2. 通知用户补救课已生成
3. 等待用户完成
4. 复诊（快速3题）
5. 复诊批改 → 通过则进主课，否则继续补救或降级Bloom

✅ **Final CHECKPOINT**:
```markdown
## ✅ Step 3.5 Complete — All pre-assessment checks passed
```

---

### Step 4: 文件驱动交互式学习 (File-Based Interactive Learning)

🚧 **GATE**: Step 3.5 complete（诊断已完成或已跳过）；学习目录存在，当前 lesson index 已确定；`session_state.json`（含 `learner_model`）已读取。

**学习者模型感知**：每次进入 Step 4 时，自动读取 `session_state.json` 的 `learner_model`：
- `bloom_target`：当前目标认知层级（用于指导习题难度和讲解深度）
- `overall_confidence_bias`：整体自信度偏差（用于选择教学策略——overconfident 用户需要更多脚手架，underconfident 用户需要更多鼓励）
- `concept_mastery`：各 concept_tag 的掌握度（用于横向概念对比时识别潜在混淆点）

**反事实论证模式解析**（非 BLOCKING）：
1. 读取 `session_state.json` 的 `counterfactual_mode` 字段
2. 按以下优先级确定最终值：
   - 若值为 `"on"` / `"off"` / `"auto"` → 直接使用，在对话中简要确认：`"反事实论证：{模式}（继承会话设置）"`
   - 若值为 `null`（首次会话）→ ⛔ **BLOCKING**：询问用户选择：
     - `始终开启` → 写入 `"on"`
     - `始终关闭` → 写入 `"off"`
     - `自动判断` → 写入 `"auto"`
     - `仅本次开启/关闭` → 写入对应值（用户下次可重新选择）
3. `"auto"` 模式规则：
   - 本课知识类型为**原理性**（Why deeply）→ 开启
   - 本课知识类型为**概念性**（What/Why）→ 按需（仅对核心结论启用）
   - 本课知识类型为**程序性**（How）→ 关闭

🛠️ **EXECUTION**:

**4.0 反事实论证模式（`counterfactual_mode = true` 时生效）**：

在生成 Lesson、检查习题作答、回答用户问题时，额外执行以下操作：

1. **反事实假设**：每个核心结论后，追加："如果 [该概念的核心要素] 不存在或发生相反变化，会导致什么结果？这与当前现实有何逻辑冲突？"
2. **因果 vs 相关**：明确区分哪些是相关性，哪些是因果性，不得将相关关系误述为因果关系
3. **自我辩论**：每个结论后增加"反事实论证"小节：
   - 假设该结论错误，可能的原因是什么？
   - 有哪些边缘案例不符合该理论？
   - 去掉前提条件后，结论是否依然成立？

**4.0 读取诊断结果（每次生成新 Lesson 前执行）**：

读取以下数据源（优先级从高到低）：
1. `session_state.json` 的 `learner_model.concept_mastery`：各 concept_tag 的掌握度和自信度偏差
2. `lessons/prereq_diagnostic.md`（本课的诊断结果）
3. `settings/background.md` 的"诊断历史与薄弱知识点"区域
4. 检查本课知识点中是否有"薄弱知识点"记录（来自 learner_model）

若 learner_model 中记录的 confidence_bias = "过度自信" → 在 Lesson 中额外增加 Worked Example
若 learner_model 中记录的 confidence_bias = "谨慎型" → 在讲解中增加鼓励性话语（如"你的判断值得信任，只需补充具体步骤"）
若 learner_model 中记录的 confidence_bias = "校准良好" → 保持标准讲解节奏
4. 若有快速回顾标记 → 在 Lesson 文件的 `### 〇、知识回引` 之前插入"### 〇、快速回顾"小节：
   ```markdown
   ### 〇、快速回顾

   > 诊断中发现你对"{missing_concept}"还不够清晰，这里先用一分钟补充一下：
   >
   > {用 2-3 句话 + 一个类比快速讲解缺失的概念}
   >
   > 了解这一点后，我们正式开始本课。
   ```
5. 检查 background.md 中是否有 Bloom 层级下调记录，若有，在 Lesson 文件元信息中标注实际目标层级

**4.1 逆向设计（生成新 Lesson 时执行）**：
1. 读取 `${SKILL_DIR}/references/bloom-taxonomy.md` 和 `${SKILL_DIR}/references/socratic-method.md`
2. 读取用户背景与教学偏好：
   - 读取 `${PROJECT_DIR}/settings/background.md` 获取基础背景和"教学偏好"区域
   - 偏好字段（教学语言、课时长度、题目数量、挑战题、反事实论证、学习模式）按以下优先级确定最终值：用户口头补充 > `background.md` 配置 > `session_state.json` 会话级覆盖 > 系统默认值
   - 若本次调用时用户补充了背景信息，与文件内容合并；冲突处以用户补充为准
3. 明确本节课目标："本节课结束后，用户应能解决什么具体问题？"
4. 从资料中提取知识点，结合历史记录和用户背景规划路径，确定目标布卢姆层级
5. **识别知识类型，匹配讲解策略**：

   对本课核心知识点，按以下规则判断知识类型并选择讲解策略：

   | 知识类型 | 判断规则 | 讲解策略 |
   |---------|---------|---------|
   | **概念性**（What/Why） | 核心问题是"X 是什么"或"为什么需要 X"（如：导数的定义、为什么需要 Transformer） | **动机铺垫** → 概念引出 → 直觉类比 → 形式化定义 |
   | **程序性**（How） | 核心问题是"怎么用 X"或"X 的操作步骤"（如：链式法则的使用、Git rebase 操作） | **规则陈述** → 分步演示 → 变式练习 |
   | **原理性**（Why deeply） | 需要数学推导、逻辑证明或机制分析（如：反向传播推导、操作系统调度策略） | **问题驱动** → 逐步推导 → 关键步骤标注 → 回顾总结 |

   > **判断原则**：一个 Lesson 可能包含多种类型的知识点，以**占比最大的类型**决定主讲解策略。次要类型的知识点在讲解中穿插，不需要严格遵循其对应策略。
   >
   > **不要为程序性知识硬编叙事**：步骤类知识需要的是清晰拆解，不是故事铺垫。
   > **不要为事实记忆类知识过度铺垫**：API 参数、公式速查等直接用结构化表格/清单呈现。
6. **生成概念标签（Concept Tags）**：为每个知识点生成一个简短、机器可读的 `concept_tag`（格式：`{topic}-{concept-name}`，如 `stm32-gpio-mode`、`c-pointer-arithmetic`）。每个 tag 唯一对应一个核心概念，用于绑定诊断题、lesson 元信息和 learner_model。
7. **识别前置依赖（Prerequisites）**：对每个 concept_tag，查询 roadmap_status.md 中哪些已学 lesson 包含相同的 concept_tag 或其相关概念。填写 `prerequisites: [lesson_{N}]`，若没有前置依赖则填写 `prerequisites: []`。
8. **查询学习者模型（Conditional）**：若 session_state.json 的 learner_model.concept_mastery 中已有相关 concept_tag 的记录，在 lesson 元信息中标注"⚠️ 该用户对此相关概念有薄弱记录（confidence_bias: {偏差类型}）"，并在讲解中针对性加强。

**4.2 Lesson 文件生成**：

1. 读取 `${SKILL_DIR}/templates/lesson-template.md`
2. 按模板生成 `${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/lessons/lesson_{index}.md`，包含：
   - **元信息**：目标认知层级、知识类型与讲解策略、**概念标签（concept_tags）**、**前置依赖（prerequisites）**（均来自 4.1 第 6-8 步）
   - **学习目标**：使用有序列表（`1. 2. 3.`），不加"本节课结束后，你应该能够："等引导语
   - **知识回引与路径面包屑**（讲解内容的第一个段落 `### 〇、知识回引`）：
     - 面包屑格式：`> 路径：\`已学课A\` → \`已学课B\` → **\`本课（本课）\`** → \`下一课\``
     - 面包屑仅展示与本课相关的前后 2-3 课，不需要展示完整 roadmap
     - 面包屑下方紧跟回引正文（遵循 Step 4.5 第 7 条的对比方向规则）
   - **## 精讲（含 Worked Example）**：
     - 按 4.1 第 5 步确定的讲解策略组织内容结构
     - 含 `> **资料原文**：` 引用，适配用户背景的深度与用词
     - **Worked Example 示范**（每课 1 个）：完整展示解题过程，每步标注"这一步为什么这样做"
   - **## 渐进训练（含 Faded Completion Practice）**：
     - 2-3 道 Completion Practice 题，每题给出部分解题步骤（逐步淡出），要求用户补全空缺步骤
     - 适用于程序性知识和原理性知识；对于概念性知识，可改为"填空式概念辨析"
   - **## 掌握测试（含新情境题）**：
     - 3 道新情境题，**必须使用与精讲和训练不同的背景/表达方式**
     - 测试题不得直接出现在训练题中——这是 retrieval practice 的核心要求
     - 若本课无新情境可出，可用"换问法"（同一问题换不同问法）

   **诊断路由条件生成（Conditional Content）**：

   | 诊断路由 | 额外生成 | 省略生成 |
   |---------|---------|---------|
   | **Skip** | 精讲压缩版（保留要点 + 1个 Worked Example） | Completion Practice 可减少 |
   | **Compact** | 标准结构 | — |
   | **Full** | 标准结构（Works Example 额外详细） | — |
   | **Remedial** | 先前置补救课，完成后再生成主课（完整结构） | — |

   **横向概念对比（条件触发）**：在生成讲解内容时，若本课知识点存在以下情况之一，则在讲解中增加一个"概念辨析"段落（对比表 + 边界案例）：
   - 与前几课已学概念容易混淆（如：可导 vs 连续、栈 vs 队列）
   - 与同领域相关概念有对比价值（如：监督学习 vs 无监督学习）
   - 用户在 learner_model 中暴露了相关概念的 misconception_tags

**4.2.1 生成后自检（强制执行）**：
Lesson 文件写入完成后，逐条核查讲解内容与习题中的每个细节：

| 情况 | 处理方式 |
|------|---------|
| 直接引用资料原文 | 保留 `> **资料原文**：` 引用块 + `[来源：{章节}]`（紧跟引用块） |
| 超出资料范围的补充内容 | 在该句/段末尾标注 `[⚠️ 当前资料未涉及此内容]` |
| 正文中基于资料的讲解/改写 | **不在正文中逐句标注**，改为在每个 `###` 大节末尾统一列出：`> 📖 本节参考：{章节1}、{章节2}` |

> **原则**：来源标注服务于可追溯性，但不应打断阅读流。正文中只出现**资料原文引用**和**资料未涉及警告**两种标注，其余来源在节尾汇总。

**来源标注完成后，继续执行以下多维度质检（逐条核查，不通过则修正后再写入文件）**：

**✅ 质检清单**：

| # | 检查项 | 判定标准 |
|---|--------|---------|
| 1 | 内容准确性 | 所有知识点可追溯到原材料或已标注"资料未涉及" |
| 2 | 难度适配 | 讲解深度、用词、举例与用户背景匹配（不低幼也不超纲） |
| 3 | 布卢姆层级匹配 | 习题确实考察本课声明的目标认知层级，而非更低层级 |
| 4 | 讲解有层次 | 内容有清晰的逻辑推进（因果/递进/对比），不是信息平铺堆砌 |
| 5 | 习题有区分度 | 每道习题考察不同侧面或不同难度，不是换皮重复 |
| 6 | 推理链完整 | 从前提到结论的每一步都显式写出，无逻辑跳跃 |

**🚫 教学绝对禁区（出现任何一条即修正）**：

| # | 禁止行为 | 说明 |
|---|---------|------|
| 1 | 用术语解释术语 | 如用"闭包是词法作用域的延续"解释闭包——循环定义，读者无法从中获得新信息 |
| 2 | 跳过推理中间步骤 | 如"由 A 显然可得 C"——必须写出 A→B→C 的每一步 |
| 3 | 用"显然""不难看出""容易证明"掩盖逻辑跳跃 | 这些词是"我懒得解释"的伪装，在教学中绝对禁止 |
| 4 | 习题与讲解内容不匹配 | 习题考察的知识点必须在本课讲解中覆盖过 |
| 5 | 过度概括导致信息密度为零 | 如"这是一个非常重要的概念，在很多领域都有应用"——空话，必须具体 |
| 6 | 编造函数名、类名、文件路径、API 参数 | 所有代码符号必须在学习资料中实际存在或明确标注为示意 |
| 7 | 讲解中引入未经铺垫的前置概念 | 如果用到了本课未讲、前几课也未覆盖的概念，必须先做最小化解释 |

**📐 排版可读性规则（生成 Lesson 时强制执行）**：

| # | 规则 | 示例 |
|---|------|------|
| 1 | **序号列表独占一行**：使用 ①②③ 或 1. 2. 3. 列举时，每项必须独占一行，不得将多项挤在同一行 | ① 第一点；<br>② 第二点 |
| 2 | **逻辑段落用空行分隔**：不同逻辑层次（问题陈述 / 列举 / 分析 / 结论）之间用空行断开，不要写成一整段 | 问题：……<br><br>① ……<br>② ……<br><br>结论：…… |
| 3 | **结论金句独立成段**：总结性的关键结论（通常加粗）单独成段，不附在分析段落末尾 | **多用 2 根线，换来了 10-100 倍的速度提升。** |
| 4 | **长句拆短**：单句超过 80 字时，寻找语义断点拆为两句或用破折号/分号断开 | — |
| 5 | **表格优先于长句并列**：3 个以上并列项的对比，用表格而非逗号分隔的长句 | — |
| 6 | **代码块前后留空行**：代码块（含行内代码引用的完整语句）的上下各留一个空行 | — |
| 7 | **反事实论证格式**：`**反事实论证**：{问题}` 后空一行，再写分析段落，分析与结论之间再空一行 | 见 lesson_4 §1.2 |

自检完成后更新文件，**不在对话中展示自检结果**，仅在通知中附加一行自检摘要：
```
🔍 自检完成：{N} 处已标注来源，{M} 处标注"当前资料未涉及"，质检 {P}/6 项通过，禁区 0 项触发
```

3. 生成后，**不在对话中展示课程内容**，仅发送通知：
   ```
   ✅ Lesson {index} 已生成！

   📄 文件位置：`./learning-history/${topic_name}_${timestamp}/lessons/lesson_{index}.md`

   请阅读该文件，在"我的答案"区域填写你的答案，保存文件后，在对话窗口告诉我"已完成"。
   ```

⛔ **BLOCKING**: 等待用户在对话中说"已完成"、"做完了"、"写完了"等表述。

**4.3 答案检查（用户说"已完成"后执行）**：

1. 读取 `lesson_{index}.md`，提取所有"我的答案"区域内容，分两类处理：
   - **渐进训练（Completion Practice）**：Completion Practice 1-N（补全淡出步骤）
   - **掌握测试（Mastery Test）**：测试题 1-N（新情境独立解题）
2. 若所有"我的答案"区域均为空 → 提示用户先去文件中填写，重新 BLOCKING
3. **渐进训练批改（Completion Practice 部分）**：
   - 评估方式：用户是否正确填写了空缺步骤？每填对一个得 1 分
   - 结果：统计 Completion Practice 正确率
4. **掌握测试批改（Mastery Test 部分）**：

   **双维度评估每道题**：

   | 维度 | 判定标准 |
   |------|---------|
   | 正确性 | 答案的结论/结果是否正确 |
   | 解释完整性 | 答案是否包含关键推理步骤，而非只有结论 |

   评估结果分为三档：
   - **完全正确**：结论正确 + 解释完整 → 给予肯定
   - **部分正确**：结论正确但解释缺失关键步骤，或结论有小误但思路正确 → 指出不足
   - **错误**：结论错误且思路偏离 → 执行错误自解释脚手架

5. **错误自解释脚手架（渐进训练和掌握测试均适用）**：

   当答案为"部分正确"或"错误"时，在给出初步反馈后，追加半结构化追问：
   ```
   💡 错误分析（请在对话中回答）：
   你觉得这个错误属于以下哪种类型？
   ① **概念理解偏差** — 你对某个核心概念的理解本身就有偏差
   ② **步骤/程序遗漏** — 你知道怎么做，但漏掉了某个关键步骤
   ③ **条件边界没注意** — 你没有仔细看清题目条件或忽略了边界情况
   ④ **计算/符号失误** — 思路对，但手滑了（粗心错误）
   ```
   - 收到用户回答后，根据类型提供针对性引导（不在 lesson 文件中修改）
   - 若用户选择"① 概念理解偏差"，在下一课开头针对性复习相关 concept_tag
   - 若用户选择"② 步骤遗漏"，提供部分步骤框架让用户补全
   - 若用户选择"③ 条件边界"，引导重新审题
   - 若用户选择"④ 计算失误"，确认即可，视为基本掌握
   - 若用户无法判断类型 → 苏格拉底式追问

6. **掌握判定**：

   | 部分 | 权重 | 达标标准 |
   |------|------|---------|
   | 渐进训练（Completion Practice） | 40% | ≥ 60% 步骤填对 |
   | 掌握测试（Mastery Test） | 60% | ≥ 60% 达到"完全正确"或"部分正确" |

   综合掌握度 = 渐进训练分 × 0.4 + 掌握测试分 × 0.6

   | 综合掌握度 | 结果 | 行动 |
   |-----------|------|------|
   | ≥ 80% | **掌握** | 进入下一课 |
   | 60-79% | **基本掌握** | 进入下一课，但在下一课开头补充缺失知识点 |
   | < 60% | **未掌握** | 重新尝试掌握测试（不重做 Completion Practice） |

   标注为"⭐ 挑战题"的习题不计入掌握判定。
7. **批改结果持久化 + learner_model 更新**（掌握判定完成后立即执行）：
   - 在每道题的"我的答案"区域下方，追加批改块，**每条逐项评价必须以状态符号开头**：
     ```
     > **批改 ⭐⭐⭐⭐（{score}/5）**
     > - ✅ {正确的点}
     > - ⚠️ {部分正确/小瑕疵}
     > - ❌ {错误的点}
     ```
     状态符号规则：✅ 完全正确 | ⚠️ 方向对但有瑕疵/不完整 | ❌ 错误
   - 在 lesson 文件的 `## 掌握度反馈` 区域，追加评分汇总表：
     ```
     ## 掌握度反馈

     ### 渐进训练（Completion Practice）
     | 题目 | 得分 |
     |------|------|
     | Completion Practice 1：{title} | ✅/⚠️/❌ |
     | Completion Practice 2：{title} | ✅/⚠️/❌ |
     | **小计** | **{CP_correct}/{CP_total} = {CP_rate}%** |

     ### 掌握测试（Mastery Test）
     | 题目 | 正确性 | 解释完整性 | 综合 |
     |------|--------|-----------|------|
     | 测试题 1：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | 测试题 2：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | 测试题 3：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | **小计** | — | — | **{MT_avg}/5** |

     ### 综合掌握度
     | 部分 | 得分 | 权重 |
     |------|------|------|
     | 渐进训练 | {CP_rate}% | 40% |
     | 掌握测试 | {MT_rate}% | 60% |
     | **综合** | **{final_rate}%** | 100% |

     **判定**：✅掌握 / ⚠️基本掌握 / ❌未掌握
     ```
   - **更新 learner_model**：对每个 concept_tag，更新 `session_state.json` 的 `learner_model.concept_mastery[concept_tag]`：
     - `test_count` += 1
     - `correct_count` += 1（若测试题达到"完全正确"）
     - `mastery_level` ← 根据掌握度更新
     - 若错误自解释中用户选择了"概念理解偏差"，在 `misconception_tags` 中追加相关标签

**4.4 动态支架**：

**降级触发**（满足任一条件）：
- 用户连续两次回答"不知道"或表现困惑
- 用户答案方向完全偏离（非粗心，而是概念理解错误）
- Reflection 中认知难度 ≥ 4

**降级策略（按优先级尝试，不只是降布卢姆层级）**：

| 策略 | 适用场景 | 操作 |
|------|---------|------|
| 换角度讲解 | 用户理解了部分但卡在某个点 | 用类比、可视化描述、生活化例子重新解释同一概念，不降低层级 |
| 分步拆解 | 用户面对的问题太大，不知从何下手 | 将复杂问题拆为 2-3 个更小的子问题，逐步引导 |
| 提供脚手架 | 用户有思路但无法完整表达 | 给出部分答案框架（如推导的前两步），让用户补全关键部分 |
| 降低布卢姆层级 | 以上策略无效，用户仍无法推进 | 从"分析/应用"退回"理解/记忆"，先确认基础再重新推进 |

> **原则**：优先保持当前认知层级不变，通过换讲法解决问题；只有在确认用户基础不牢时才降级。

**升级触发**（满足任一条件）：
- 用户连续两课一次性全部答对且解释完整
- Reflection 中认知难度 ≤ 1

**升级操作**：下一课主动提升布卢姆层级，或在习题中增加 1 道高于当前目标层级的挑战题（标注为"⭐ 挑战题"，不计入掌握判定）

**补救课与偏题分支文件命名规则**：

当动态支架的降级策略仍无法解决问题（连续 2 课 mastery < 60%），或用户明确要求深入偏题时，可生成非主线 lesson 文件：

| 类型 | 文件命名 | 触发条件 | roadmap 标记 |
|------|---------|---------|-------------|
| 🔧 补救课 | `lesson_{N}_remedial.md` | 连续 2+ 课 mastery < 60%，需回顾基础 | `🔧 补救课` |
| 🔀 偏题分支 | `lesson_{N}_branch.md` | 用户要求深入偏题探索 | `🔀 分支课` |

生成后必须同步更新：
1. `roadmap_status.md` 的"学习历史"表格：追加补救课/分支课行，备注触发原因
2. `roadmap_status.md` 的"路线调整记录"表格：记录调整类型、触发原因、影响
3. `_ai_context.md`：追加教学决策日志条目

> **补救课/分支课不计入 `session_state.json` 的 `current_lesson` 编号递增**，它们是主线的插入节点。完成后回归主线时，`current_lesson` 继续从中断处递增。

**4.4.1 主线优先与偏题处理（强制执行）**：

回答用户提问前，先对照 `roadmap_status.md` 中的当前主线任务判断相关性：

| 判断结果 | 处理方式 |
|---------|---------|
| 与主线强相关 | 正常回答，可深入展开 |
| 与主线弱相关或无关 | 执行偏题处理流程（见下） |

**偏题处理流程**：
1. 在 `summary.md` 的 `⏳ 待解决` 区域追加记录：
   ```
   - {用户问题摘要}（待主线任务结束后再解决）
   ```
2. 在对话中回复：
   ```
   这是一个很有趣的问题，但与我们本次的学习目标不强相关。我已经帮你记录下来了，待我们完成主线任务后再回来探索。
   ```
3. 将对话引导回当前主线任务

**4.5 进度更新（每个 Lesson 完成后执行）**：
1. 更新 `summary.md`：
   - 新增本次结论与未竟难点
   - **错题记录持久化**：将 4.3 答案检查中评估为"部分正确"或"错误"的习题，追加到 `summary.md` 的"错题记录"表格中，每行包含：课时、题号、错误摘要（一句话概括错在哪）、错误类型（概念/程序/推理）、状态（❌ 未纠正）。若用户在重新尝试后纠正了错误，将对应行的状态更新为 ✅ 已纠正
   - **复习队列更新**：将"部分正确"或"错误"的习题追加到 `review_queue.json` 的 `items` 数组，字段包括 `id`（`review_{NNN}`）、`lesson`、`question_index`、`topic_tag`、`first_wrong_at`、`corrected_at`（若已纠正）、`next_review_at`（纠正后 +1 天）、`review_count`（0）、`status`（`"pending"` 或 `"resolved"`）。纠正后的条目：`next_review_at` = 纠正时间 + 1 天，`status` = `"pending"`；复习通过后：`review_count` += 1，`next_review_at` = 当前时间 + `2^review_count` 天（间隔重复）
2. 更新 `roadmap_status.md`：更新进度百分比与导航坐标
3. **更新 `_ai_context.md`**：
   - 更新断点恢复信息（最后完成课时、当前课时状态、未纠正错题数）
   - 更新用户画像快照（根据本课答题表现修正错误模式分析、认知偏好）
   - 追加教学决策日志（如触发了动态支架、插入了补救课等关键决策）
4. **更新 `session_state.json`（状态唯一权威源，v2.0）**：
   - `current_lesson` ← 下一课编号
   - `phase` ← `"learning"` / `"review"` / `"completed"`（视当前阶段）
   - `last_completed_lesson` ← 刚完成的课时编号
   - `mastery_passed` / `mastery_failed` ← 累加本课答题结果
   - `mastery_rate` ← `mastery_passed / (mastery_passed + mastery_failed)`
   - `wait_reason` ← `"awaiting_answer"` / `null`（视是否等待用户答题）
   - `updated_at` ← 当前时间戳
   - 若为 Git 仓库学习：`repo_commit_hash` ← 当前 HEAD commit hash
5. **追加 `metrics.json` 事件**（若文件不存在则从 `metrics-template.json` 初始化）：
   ```json
   {
     "event": "lesson_completed",
     "timestamp": "<ISO 8601>",
     "lesson": <lesson_index>,
     "mastery_passed": <本课通过题数>,
     "mastery_failed": <本课失败题数>,
     "scaffold_triggered": <true/false>,
     "counterfactual_used": <true/false>,
     "review_triggered": <true/false>,
     "remedial_inserted": <true/false>
   }
   ```
6. **状态一致性自检（强制执行）**：
   写入所有文件后，逐条验证以下不变量，任何一条不通过则立即修正：

   | # | 不变量 | 检查方式 |
   |---|--------|---------|
   | 1 | `session_state.json` 的 `current_lesson` 与 `lessons/` 目录下实际存在的最新 lesson 文件编号一致 | 列出 `lessons/` 目录，取最大编号对比 |
   | 2 | `_ai_context.md` 的“当前课时状态”与 `session_state.json` 的 `phase` 一致 | 读取两个文件对比 |
   | 3 | `roadmap_status.md` 的"当前课时"与 `session_state.json` 的 `current_lesson` 一致 | 读取两个文件对比 |
   | 4 | `summary.md` 的"已完成课时"与 `session_state.json` 的 `last_completed_lesson` 一致 | 读取两个文件对比 |
   | 5 | 若 `phase` 为 `"learning"` 且 `current_lesson` > 0，则对应 lesson 文件必须存在 | 检查文件是否存在 |

   > **自检结果不在对话中展示**，仅在 CHECKPOINT 中附加一行：`🔒 状态自检：{N}/5 项通过`

6. **读取 Reflection 反馈**：检查 `lesson_{index}.md` 中 `## Reflection` 区域，若用户填写了认知难度或需要澄清的内容：
   - 认知难度 ≥ 4 → 触发 4.4 动态支架的降级策略
   - 认知难度 ≤ 1 → 触发 4.4 动态支架的升级机制
   - 用户提出需要澄清的内容 → 在下一课开头增加针对性补充讲解
7. 若话题偏离主线 → 提示："我们正在偏离原定目标，是否将其作为新分支记录，还是回到主线？"
8. **每 3 课审视 Roadmap（当 lesson_index 为 3 的倍数时执行）**：
   - 读取 `summary.md` 中的"待攻克难点"和"错题记录"
   - 读取 `roadmap_status.md` 中后续待学习的知识点列表
   - 判断：是否存在持续未解决的薄弱前置知识？若是，在 roadmap 中当前位置插入一节补救课程（标注为"🔧 补救课"），优先于后续新内容
   - 判断：已完成的课程中是否暴露出 roadmap 未覆盖的重要知识缺口？若是，在 roadmap 中追加对应知识点
9. **知识回引与横向对比（每课执行）**：在生成下一个 Lesson 时，检查本课知识点与其他知识点的关联，并根据**对比方向**选择不同策略：

   **对比方向规则**：
   | 方向 | 定义 | 允许的形式 | 禁止的形式 |
   |------|------|-----------|-----------|
   | **回溯对比**（本课 vs 已学概念） | 对比对象在前几课中已完整讲授 | 完整对比表、深度分析、选型指南 | 无 |
   | **前向预告**（本课 vs 未学概念） | 对比对象将在后续课程中才学习 | 仅限一句话结构性提示（如"I2C 用最少的线换协议复杂度，后面我们会学另一种做了相反取舍的总线"） | ❌ 禁止引入未学概念的专有术语，❌ 禁止参数级对比表 |
   | **课内对比**（本课多个概念互比） | 对比对象在同一课中讲授 | 完整对比表、深度分析 | 无 |

   **执行逻辑**：
   - 若本课概念是前几课某概念的深化、应用或对立面 → **回溯对比**：在讲解开头增加回引 + 插入对比表
   - 若本课概念与后续未学概念有关联 → **前向预告**：仅用一句话点出设计哲学差异，激发好奇心但不增加认知负荷
   - 若无明显关联 → 不强行回引或对比，保持讲解简洁
   - 若当前课时为 roadmap 中标注的"横纵交汇课" → 不引入新知识，整合已学内容，必须包含完整矩阵对比表 + 选型决策树 + 真实场景选型习题
10. 生成下一个 Lesson 文件，重复 4.2 流程

✅ **Step 4 完成**：Lesson {index} 已掌握（X/Y 题），详情见文件。

→ **继续下一 Lesson** 或 **用户退出 → 进入 Step 5**

---

### Step 5: 生成学习报告 (Learning Report)

🚧 **GATE**: 用户明确表示学习完成或阶段性退出；`summary.md` 和 `roadmap_status.md` 已更新至最新状态。

🛠️ **EXECUTION**:

1. 读取 `${SKILL_DIR}/templates/report-template.md`
2. 读取 `summary.md` 和 `roadmap_status.md` 获取完整学习数据
3. 生成报告文件：`${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/report.md`，包含：
   - **目标达成度**：初始目标 vs 实际进度的可视化对比
   - **掌握明细表**：Lesson 编号、名称、认知层级评分（1-5 ⭐）、后续建议
   - **能力增长图谱**：描述用户从"不会"到"掌握"的认知迁移路径
   - **进阶规划**：基于 `summary.md` 中的难点，推荐下一个关联学习主题

4. **GitHub 项目学习可选工程产物**（仅当学习资料为 GitHub 项目/本地目录时）：
   - 若用户在学习过程中表达了"想参与贡献"、"想改代码"、"想读源码"等意图，按需生成：
     - `architecture_map.md`（从 `architecture-map-template.md`）：模块依赖 Mermaid 图 + 数据流 + 技术栈
     - `file_reading_order.md`（从 `file-reading-order-template.md`）：推荐阅读顺序 + 可跳过文件 + 首次贡献建议
   - 这些文件生成在会话目录根级（与 `report.md` 同级）
   - 若用户未表达相关意图，则不生成

报告已生成：
- 📄 `report.md`：`./learning-history/${topic_name}_${timestamp}/report.md`
- 目标达成度：{N}/6 Lessons | 掌握率：{X/Y} 题 | 用时：{duration}

→ **进入待命状态**，随时可以继续学习或退出。
