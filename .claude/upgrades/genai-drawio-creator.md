# 升级需求备忘录

## 待集成：GenAI-DrawIO-Creator

**状态**: ⏳ 暂缓（当前 SKILL.md 够用）

**触发条件**: 当以下场景变频繁时

- [ ] 批量生成教材图表（每周 > 5 张）
- [ ] 需要 Kubernetes/AWS/Azure/BPMN 等专业 shape 库
- [ ] 手动调图频率过高（每次生成后需调整 > 3 处）
- [ ] 图的质量要求提高（需 VLM 视觉校验）

---

## GenAI-DrawIO-Creator 能力

| 能力 | 说明 |
|------|------|
| **语义校验** | AI 生成后对比 vertex label 与用户请求，缺哪个自动反馈 |
| **结构校验** | 11 项检查 + 24 步自动修复 |
| **视觉校验** | VLM 渲染成位图检查重叠/布局问题 |
| **非破坏性迭代** | 按 cell ID 编辑，保留手工优化 |
| **Shape 库** | 34+（AWS、GCP、Azure、K8s、BPMN、UML、Cisco、Material Design 等） |

**GitHub**: https://github.com/tuoxie2046/GenAI-DrawIO-Creator
**论文**: KDD 2025

---

## 集成方案

```bash
# 1. 安装
git clone https://github.com/tuoxie2046/GenAI-DrawIO-Creator.git
cd GenAI-DrawIO-Creator
pip install -e .

# 2. 配置 MCP server 或 CLI hook
# 在 settings.json 中添加调用
```

---

## 决策 Checklist

- [ ] 出图频率是否足够高？
- [ ] 当前 SKILL.md 规则是否已不够用？
- [ ] 是否需要专业 shape 库？
- [ ] 团队是否接受额外依赖？

**何时激活**: 满足任意 2 条时

---

*创建日期: 2026-04-16*
