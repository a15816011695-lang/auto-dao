# Lesson 1: 文件驱动学习原理

**时间**: 2026-04-10 14:10
**主题**: 黄金样例
**目标认知层级**: 理解 (Bloom Level 2)

---

## 学习目标

1. 理解 auto-dao 文件驱动学习的核心原则
2. 区分"权威状态源"与"派生视图"的角色

---

## 讲解内容

### 一、文件驱动原则

auto-dao 的所有课程内容、习题和答案都通过文件交互，而非对话窗口。

> **资料原文**：
> "All lesson content, exercises, and answers live in files."

[来源：CLAUDE.md §Core Concepts]

### 二、状态管理

`session_state.json` 是唯一的机器可读状态权威源。`summary.md` 和 `roadmap_status.md` 是派生视图。

> 📖 本节参考：SKILL.md §状态管理原则

---

## 课后习题

### 习题 1：文件驱动的核心好处

为什么 auto-dao 选择文件驱动而非对话驱动？请用自己的话解释。

[来源：CLAUDE.md §Core Concepts]

**我的答案**：

文件驱动可以避免 AI 幻觉，因为所有内容都持久化到文件中，用户可以随时回看和验证。同时也便于断点恢复。

> **批改 ⭐⭐⭐⭐⭐（5/5）**
> - ✅ 正确指出了防幻觉的好处
> - ✅ 正确提到了断点恢复的优势

---

### 习题 2：权威源与派生视图

当 `session_state.json` 与 `summary.md` 的进度不一致时，应以哪个为准？为什么？

[来源：SKILL.md §状态管理原则]

**我的答案**：

应该以 summary.md 为准，因为它包含更详细的信息。

> **批改 ⭐⭐（2/5）**
> - ❌ 应以 session_state.json 为准，它是唯一权威源
> - ⚠️ summary.md 确实包含更多补充信息，但核心进度字段必须以 session_state.json 为准

（用户纠正后重新作答：以 session_state.json 为准 → ✅ 已纠正）

---

## Reflection

**认知难度** (1-5): 2
**需要澄清的内容**: 无

## 本节要点总结

1. 文件驱动 = 防幻觉 + 可追溯 + 断点恢复
2. session_state.json 是唯一权威源
3. Markdown 文件是派生视图，允许追加补充信息
