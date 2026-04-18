# drawio 画图工作流

AI 生成 drawio XML 时，优先使用语义正确的 shape 而非通用矩形。drawio 官方 shape 库丰富，数据库用 cylinder3，决策用 rhombus，P&ID 用 shape=mxgraph.pid2valves.*。

## 生成规则

### 语义 Shape 优先

| 场景 | Shape | 说明 |
|------|-------|------|
| 数据库/存储 | `shape=cylinder3` | 圆柱体表示数据容器 |
| 决策/条件判断 | `shape=rhombus` | 菱形表示分支 |
| 流程/处理 | `shape=rect` | 通用矩形 |
| API/服务 | `shape=mxgraph.azure.*` | 云服务专用 |
| 网络拓扑 | `shape=mxgraph.cisco.*` | Cisco 设备库 |
| Kubernetes | `shape=mxgraph.k8s.*` | K8s 资源 |
| BPMN | `shape=mxgraph.bpmn.*` | BPMN 流程 |

### XML 结构要求

生成 drawio XML 必须满足：

```
1. 良构 XML：所有标签正确闭合
2. mxfile 为根元素
3. 每个 diagram 有唯一 id
4. 根节点包含 mxCell id="0" 和 mxCell id="1" parent="0"
5. 所有 cell id 唯一
6. 内容 cell 必须标记 vertex="1" 或 edge="1"
7. 边的 source/target 指向存在的 vertex id
8. style 用 key=value 格式
9. 非矩形 shape 必须有匹配的 perimeter
```

### 关键禁令

**禁止 XML 注释**：永远不要在生成的 XML 中包含 `<!-- -->`。XML 注释被严格禁止——浪费 token、可能引发解析错误、在 diagram XML 里毫无用途。

## 官方参考文档

- [drawio Style Reference](https://www.drawio.com/doc/faq/drawio-style-reference)：所有 shape + style + 色板
- [jgraph 官方 XML Reference](https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md)：实战 XML 结构
- [AI 生成专用指南](https://www.drawio.com/doc/faq/ai-drawio-generation)：AI 生成最佳实践

## 校验清单

生成后自检：

- [ ] XML 良构，可被解析
- [ ] mxfile 作为根元素
- [ ] 每个 diagram 有唯一 id
- [ ] 根里有 mxCell id="0" 和 mxCell id="1"
- [ ] 所有 cell id 唯一
- [ ] 内容 cell 明确标记 vertex="1" 或 edge="1"
- [ ] 边的 source/target 指向存在的 vertex
- [ ] 无 XML 注释
- [ ] style 格式正确

## 使用方式

```bash
# 打开 draw.io 编辑器
mcp__drawio__open_drawio_xml

# 用 Mermaid 生成
mcp__drawio__open_drawio_mermaid

# 用 CSV 数据生成
mcp__drawio__open_drawio_csv
```

## 节点尺寸硬性规则 (必须遵守)

### 默认尺寸

- 普通节点 (1-4 字): width=80, height=40
- 中等节点 (5-10 字): width=120, height=40
- 长文本节点 (10+ 字): width=160, height=48
- 菱形决策节点: width=100, height=60 (菱形视觉上需要多一点高度)
- 容器/分组: 只在需要包裹子元素时才用, padding 左右各 20、上下各 30

### 字号

- 所有节点标签统一 fontSize=14 (不要写 12, 太小; 不要写 16, 在密集图里太挤)
- 标题/分组名可以 fontSize=16; fontStyle=1 (粗体)
- 边上的标签 fontSize=11

### 长文本处理

- 标签超过 12 个字 → 必须加 `whiteSpace=wrap;html=1`
- 千万不要靠"把框画大"来容纳长文本, 要靠 wrap
- 不要手工换行 (\n), 让 wrap 自动处理

### 间距

- 节点之间水平间距 ≥ 60, 垂直间距 ≥ 40
- 不要为了"紧凑"把节点贴在一起, 连线会打架

### autosize 属性

drawio 有个被严重低估的 style 属性: `autosize=1`。打开它, 节点会根据实际文本内容自动调整大小, 不用 AI 猜尺寸。

```xml
style="rounded=1;whiteSpace=wrap;html=1;autosize=1;fontSize=14;"
```

## 高级方案

如需自动校验 + 自修复流水线，集成 [GenAI-DrawIO-Creator](https://github.com/tuoxie2046/GenAI-DrawIO-Creator)：

- 支持 34+ shape 库（AWS、GCP、Azure、Kubernetes、BPMN、UML、Cisco 等）
- 语义校验：检查请求组件是否都存在
- 多级校验：结构校验（11 项检查 + 24 步自动修复）+ VLM 视觉校验
- 非破坏性迭代：按 cell ID 编辑，保留手工优化