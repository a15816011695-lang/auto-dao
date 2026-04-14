# 🎓 auto-dao — AI 私人导师

> 能规划、能诊断、能动态调整的 AI 私人导师

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 📚 **学习路线规划** | 根据学习材料自动生成个性化学习路径 |
| 🔍 **学习诊断** | 通过习题检验掌握程度，找出薄弱环节 |
| 🔄 **动态调整** | 根据反馈自适应调整难度和进度 |
| 📝 **自动笔记** | 学习过程中自动记录要点和重难点 |
| 🌍 **跨语言教学** | 支持学习材料与教学语言不同 |
| 🎯 **文件驱动** | 所有内容保存在文件中，防止 AI 幻觉 |

---

## 📦 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/a15816011695-lang/auto-dao.git
cd auto-dao
```

### 2. 配置 API Key（可选）

编辑 `settings/.env`，填入 MinerU API Key（仅转换 PDF/Word/PPT 时需要）：

```env
MINERU_API_KEY=你的API密钥
```

👉 获取 Key：https://mineru.net/apiManage/token

### 3. 个性化配置

编辑 `settings/background.md`，填入你的背景信息：

```markdown
## 正在读的年级
大三

## 正在学习的科目、知识等
C 语言、STM32、ESP32、嵌入式 Linux

## 目前遇到的问题
C 语言基础不牢，需要完善 STM32+ESP32 技术栈
```

---

## 🚀 开始使用

在 Qwen Code 或任意 AI 助手中，直接提供学习材料并说明学习目标即可。

**示例：**
```
我想学习 STM32 开发，材料在 ./tmp/stm32-tutorial.md
我的背景：大三物联网专业，C 语言基础一般
```

AI 会自动：
1. 生成个性化学习路线
2. 创建讲义和习题
3. 批改你的习题并诊断学习情况
4. 根据反馈动态调整教学

---

## 📂 支持的学习材料

| 类型 | 示例 |
|------|------|
| Markdown 文件 | `./tmp/notes.md` |
| PDF 文档 | `./tmp/textbook.pdf` |
| Word / PPT | `./tmp/slides.pptx` |
| 图片 | `./tmp/notes.jpg` |
| 源码文件 | `./tmp/main.py` |
| 本地项目 | `./tmp/my-project/` |
| GitHub 链接 | `https://github.com/user/repo` |

---

## 🛠️ 可用 Skills

| Skill | 功能 | 说明 |
|-------|------|------|
| **learning-engine** | 主学习引擎 | 规划路线、生成讲义、批改习题 |
| **everything-to-markdown** | 文档格式转换 | PDF/Word/PPT → Markdown |
| **glossary-collector** | 术语表提取 | 提取专业词汇生成对照表 |

---

## 📁 目录结构

```
auto-dao/
├── .claude/skills/              # Skills 定义（供 AI 参考）
│   ├── learning-engine/         # 学习引擎
│   ├── everything-to-markdown/  # 文档转换
│   ├── markdown-refiner/        # Markdown 质量优化
│   └── glossary-collector/      # 术语提取
├── settings/                    # 用户配置
│   ├── .env                     # API Keys（不提交到 Git）
│   ├── .env.example             # API Keys 配置模板
│   ├── background.md            # 用户背景信息
│   └── glossary.md              # 术语表
├── learning-history/            # 学习记录（自动生成）
│   └── {topic}_{timestamp}/
│       ├── summary.md           # 学习摘要
│       ├── roadmap_status.md    # 学习路线图
│       ├── report.md            # 学习报告（学习完成后生成）
│       └── lessons/
│           └── lesson_N.md      # 第 N 课内容
├── examples/                    # 示例学习记录
└── tmp/                         # 学习材料存放处
```

---

## 💡 使用技巧

### 1. 文件驱动学习
- 所有讲义和习题保存在 `learning-history/` 的文件中
- 用户在文件中完成习题，AI 读取后批改
- **不在对话中展示课程内容**，始终保持文件驱动

### 2. 跨语言教学
- 学习材料为英文，可用中文教学
- AI 会优先使用 `settings/glossary.md` 中的术语译法

### 3. 跳读与查漏补缺
- 已有基础？AI 先出题检验掌握程度
- 完全掌握可直接跳过，否则缺啥补啥

---

## 🤝 贡献指南

欢迎贡献！

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 MIT 协议。
