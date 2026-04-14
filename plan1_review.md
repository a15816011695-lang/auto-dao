# plan1.md 修改建议评审报告

> 基于项目源码、状态文件、脚本实现的逐条交叉验证。每条建议均标注 **事实核验结果** 和 **收益判断**。

---

## 总体评价

**结论：这份 plan 的质量很高，绝大多数建议合理且有实据支撑。**

该 plan 正确识别了项目从"功能验证期"进入"工程稳定期"的转折点，建议的优先级排序也基本合理。但部分建议存在**事实偏差**或**实施成本被低估**的情况，下面逐条分析。

---

## 逐条评审

### ✅ P0：状态一致性 — `session_state.json`

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ **确认存在，且比 plan 描述的更严重** |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ✅ **全项目 ROI 最高的优化，同意** |

**我的交叉验证结果**：

plan 声称 [_ai_context.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/_ai_context.md) 说"Lesson 4 未生成"，但目录里已有 [lesson_4.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/lessons/lesson_4.md)。我验证了这一点：

- [_ai_context.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/_ai_context.md) 第 55 行：`当前课时状态 | Lesson 4 未生成` → **确实如此**
- `lessons/` 目录：**确实已存在** [lesson_4.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/lessons/lesson_4.md)（20,889 字节）
- [summary.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/summary.md) 第 40 行：`Lesson 3 已生成，待答题` → 但 roadmap 已指向 Lesson 4
- [roadmap_status.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/roadmap_status.md) 第 21 行：`当前课时 | Lesson 4`

**四个文件对"当前进度"的描述互相矛盾**，这不是偶发疏漏，而是系统性问题——因为没有单一事实源（Single Source of Truth）。

> [!WARNING]
> 补充发现：[summary.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/summary.md) 的"下次学习计划"第 1 条还写着"完成 Lesson 3 习题"，但 Lesson 3 的错题记录显示大部分已纠正。这说明 [summary.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/summary.md) 的更新粒度不够细，多个字段停留在旧状态。

**收益判断**：做一个 `session_state.json` 作为唯一机器可读状态源，其余文件从它派生更新，可以从根本上解决这个问题。**强烈建议优先实施**。

**实施建议补充**：
- 建议用 JSON 而非 YAML（Claude/AI 对 JSON 的解析更可靠）
- `session_state.json` 应放在会话目录根下，与 [summary.md](file:///f:/code/0.porject/auto-tutor/learning-history/003_stm32f103-hal_2026-04-13-09-45/summary.md) 同级
- 写入时机：每次 Lesson 生成后、答案批改后、进度更新后

---

### ✅ P0：会话一致性校验器 — `validate_session.py`

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ 确认存在 |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ⚠️ **有收益，但需注意定位** |

**合理性分析**：

plan 的逻辑链是对的：Prompt-first 项目最怕"看起来都对但状态已坏"。加一个校验脚本可以在"生成后"做不变量检查。

**但需要注意**：

1. **谁来调用它？** 如果期望 Claude 自动在每次操作后调用脚本，需要在 SKILL.md 中加入调用指令。但这会增加 token 开销和流程复杂度。
2. **更实际的方案**：不写独立脚本，而是在 SKILL.md 的进度更新步骤（Step 4.5）中加入一个"自检清单"，让 AI 在写文件前先校验不变量。这比外部脚本更轻量，也更符合 Prompt-first 项目的特性。

**收益判断**：方向对，但建议**先把校验逻辑内嵌到 SKILL.md 的 Step 4.5**，而不是急着写 Python 脚本。等状态漂移问题持续出现再升级为脚本。

---

### ⚠️ P1：拆分 learning-engine SKILL.md — 需要更谨慎

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ 609 行确实偏长 |
| 建议是否合理 | ⚠️ **方向对，但实施方案需要调整** |
| 收益是否值得 | ⚠️ **收益真实但风险也真实** |

**事实核验**：

SKILL.md 确实 609 行 / 34,823 字节，涵盖了从预处理到报告生成的全流程。plan 列出的 8 个职责确实都存在。

**但 plan 忽略了一个关键约束**：

> [!IMPORTANT]
> Claude Code 的 Skill 系统**不支持 Skill 之间的自动编排调用**。拆成 5 个子 Skill 后，主 Skill 无法用 `import` 或 `call` 的方式调用子 Skill。实际执行时，Claude 需要在一个上下文窗口内同时理解主 Skill 和所有相关子 Skill 的内容。

**这意味着**：
- 拆分不会减少 token 消耗（Claude 仍需读取所有文件）
- 拆分后**上下文分散在多个文件**，反而可能降低 AI 的遵循率
- 真正的收益在于**人类维护时**更容易定位和修改

**我的建议**：
- **不要拆成独立 Skill**，而是在 SKILL.md 内部做**章节化重构**
- 用清晰的 `---` 分隔线和 `## Module: xxx` 标题把职责分块
- 如果某个模块（如答案批改）的规则特别复杂，可以提取为 `references/grading-rules.md`，在主 SKILL 中引用
- 这样既保持了单文件的上下文连续性，又改善了可维护性

---

### ✅ P1：修复 `tmp/converted` 资源路径依赖 — 完全正确

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ **确认存在，且范围比 plan 描述的更大** |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ✅ **高收益，建议优先实施** |

**我的交叉验证结果**：

plan 只提到了 `lesson_4.md`，但实际上**所有 lesson 文件都有这个问题**：

| 文件 | 引用 `tmp/converted` 图片数量 |
|------|----------------------------|
| lesson_2.md | **8 处** |
| lesson_3.md | **6 处** |
| lesson_4.md | **3 处** |

总计 **17 处图片引用**指向 `../../../tmp/converted/` 路径。

> [!CAUTION]
> 这意味着一旦清理 `tmp/` 目录，**所有已生成的课程图片都会丢失**。学习记录将无法作为独立归档保存。

**建议**：完全同意 plan 的方案——在 SKILL.md 的 Lesson 生成步骤（Step 4.2）中增加规则：
1. 生成 lesson 时，将引用的图片复制到 `learning-history/<session>/assets/`
2. lesson 文件中的图片路径改为相对引用 `../assets/xxx.jpg`

---

### ✅ P1：`convert_to_markdown.py` 工程韧性 — 大部分正确

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ 大部分确认 |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ⚠️ **中等收益，非最优先** |

**逐项核验**：

| plan 声称的问题 | 核验结果 |
|----------------|---------|
| 所有网络请求无 timeout | ✅ **确认**：`requests.post/put/get` 均无 `timeout` 参数 |
| 无统一重试/backoff | ✅ **确认**：无任何重试逻辑 |
| `create_task_from_file()` 注释说返回 tuple 但实际返回 `batch_id` | ✅ **确认**：函数签名写 `-> tuple`，docstring 写 `Returns: (batch_id, task_id 或 None)`，但实际只 `return batch_id` |
| 项目根目录查找从 `Path(__file__).resolve()` 开始 | ⚠️ **部分正确**：代码用的是 `Path(__file__).resolve()`，这本身没问题，但确实应从 `.parent` 开始搜索（当前代码从文件自身路径开始 while 循环，第一轮会尝试在脚本所在目录找 `settings/`，虽然不会出错但浪费一轮迭代） |
| `zipfile.extractall()` 路径安全风险 | ✅ **确认**：使用了 `zf.extractall(extract_dir)` 无路径校验（Zip Slip 风险） |
| 没有 `requests.Session()` | ✅ **确认**：每个请求都创建新连接 |

**收益判断**：这些都是真实问题，但**当前项目规模下风险可控**。脚本只在文档转换时运行，不是高频调用。建议**放在 P0 之后做**，优先级排序合理。

---

### ⚠️ P1：收敛工具链 — 问题被放大了

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ⚠️ **存在，但严重性被高估** |
| 建议是否合理 | ⚠️ 部分合理 |
| 收益是否值得 | ❌ **低收益，不建议现在投入** |

**事实核验**：

- `package.json`：**仅用于提供一个 npm script 快捷命令**（`npm run convert` → 调用 Python 脚本），不是 Node.js 项目
- `node_modules/`：**仅包含 `dotenv` 一个包**（用于 `.env` 文件加载），但实际上 Python 侧已有 `python-dotenv` 依赖
- `requirements.txt`：只有 2 个依赖（`requests` 和 `python-dotenv`）

> [!NOTE]
> `node_modules/` 中的 `dotenv` 实际上**完全没有被使用**——Python 脚本用的是 `python-dotenv`。这个 `node_modules/` 可能是误装的残留。

**我的建议**：
- 删除 `node_modules/` 和 `package-lock.json`（它们是残留物）
- `package.json` 保留与否无所谓（就一个便捷命令）
- 在 README 中明确"Python utility + Prompt 仓库"即可
- **不值得花专门时间"收敛工具链"**，5 分钟清理即可

---

### ✅ P1：反事实论证持久化 — 方向正确

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ 确认 |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ✅ **中等收益，体验提升明显** |

**事实核验**：

SKILL.md Step 4 开头确实有一个 BLOCKING 询问（第 331-337 行），每次新会话都会问一次。如果做了 P0 的 `session_state.json`，可以很自然地把 `counterfactual_mode` 也存进去。

**但 plan 的"按知识类型自动启用"建议需要注意**：

SKILL.md 4.1 第 5 步已经有知识类型分类（概念性/程序性/原理性）。将反事实论证与知识类型绑定的思路是好的，但**需要用户确认这个自动策略是否符合预期**。建议：
- 默认关闭，首次使用时询问
- 用户选择后存入 `session_state.json`
- 提供"自动模式"选项（按知识类型触发）

---

### ✅ P2：文档漂移清理 — 正确但优先级可降

| 维度 | 判定 |
|------|------|
| 问题是否真实存在 | ✅ **确认存在** |
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ⚠️ **有收益，但 P0 做完后部分问题会自然解决** |

**事实核验**：

- `OUTPUT_SPEC.md` 确实没有提到 `_ai_context.md`（这个文件是后来引入的）
- `CLAUDE.md` 的目录树中**也没有 `_ai_context.md`**
- `learning-history/README.md` 只提到三个文件
- `OUTPUT_SPEC.md` 在某些地方用 `roadmap.md` 而非 `roadmap_status.md`

**建议**：等 P0 做完后，做一次统一的文档基线清理。把它作为 P0 的收尾工作而非独立任务。

---

### ✅ P2：Prompt 项目 Eval — 方向正确

| 维度 | 判定 |
|------|------|
| 建议是否合理 | ✅ 合理 |
| 收益是否值得 | ⚠️ **长期有收益，但当前阶段可延后** |

plan 建议用 `examples/learning-history` 做 fixture 跑 checklist。这比写传统单测更适合 Prompt 项目。但当前项目只有 3 个真实会话，eval 的投入产出比还不够高。建议**在 P0 和 P1 做完、项目稳定后再考虑**。

---

### ✅ "不建议投入的方向" — 完全同意

plan 列出的 4 个不建议方向（数据库、知识图谱、前端仪表盘、复杂 CI）评估准确。这些都是"听起来高级但会把项目带偏"的典型陷阱。

---

## 综合评审结论

### 建议的可信度评分

| 建议 | 问题真实性 | 方案合理性 | 收益/成本比 | 总评 |
|------|-----------|-----------|------------|------|
| P0: session_state.json | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **强烈推荐** |
| P0: validate_session.py | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 推荐（但建议内嵌到 SKILL.md） |
| P1: 拆 learning-engine | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 方向对但方案需调整 |
| P1: 修复 tmp 路径依赖 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **强烈推荐** |
| P1: 脚本工程韧性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 推荐 |
| P1: 收敛工具链 | ⭐⭐ | ⭐⭐⭐ | ⭐ | 5 分钟清理即可，不需专项 |
| P1: 反事实论证持久化 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 推荐（随 P0 一起做） |
| P2: 文档漂移 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 作为 P0 收尾工作 |
| P2: Eval | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 延后 |

### 我建议的实施顺序

如果现在只做 3 件事，我的排序与 plan 略有不同：

1. **`session_state.json`** + 修改 SKILL.md 4.5，加入状态写入和自检规则（plan 的第 1 件 + 第 2 件合并）
2. **修复 `tmp/converted` 图片路径**，增加 `assets/` 复制机制（plan 列为 P1，但我认为应提到第 2 位）
3. **SKILL.md 章节化重构**（不是拆成独立 Skill，而是在单文件内重组结构）

> [!TIP]
> 第 1 件和第 2 件可以一起做——都是修改 SKILL.md 的 Step 4 流程。修改 SKILL.md 一次，同时解决状态一致性和图片路径两个问题。
