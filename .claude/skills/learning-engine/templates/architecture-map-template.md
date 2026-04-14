# 架构图 (Architecture Map)

<!-- 可选产物：仅在 GitHub 项目学习模式中，用户表示"想参与贡献"或"想改代码"时按需生成 -->

**项目**: {project_name}
**仓库**: {repo_url}
**生成时间**: {timestamp}

---

## 模块依赖关系

```mermaid
graph TD
    A[{module_1}] --> B[{module_2}]
    A --> C[{module_3}]
    B --> D[{module_4}]
    C --> D
```

> 用 Mermaid 或文本描述均可，优先 Mermaid；如项目较小，可用文本列表替代。

---

## 核心模块说明

| 模块 | 职责 | 关键文件 | 对外接口 |
|------|------|---------|---------|
| {module_1} | {responsibility} | {key_files} | {api_surface} |
| {module_2} | {responsibility} | {key_files} | {api_surface} |

---

## 数据流概览

```
{input} → [{module_1}] → [{module_2}] → {output}
```

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 语言 | {language} | {version} |
| 框架 | {framework} | {version} |
| 构建 | {build_tool} | {version} |
