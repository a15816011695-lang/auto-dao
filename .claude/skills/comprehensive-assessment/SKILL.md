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
