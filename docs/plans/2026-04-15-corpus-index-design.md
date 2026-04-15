# 语料快速索引系统设计方案

**日期**: 2026-04-15
**状态**: 已批准
**设计人**: AI (Claude Code) + 用户确认

---

## 背景与目标

在 `tmp/converted/` 中已积累多个转换后的嵌入式/STM32 学习资料，共约 24K 行 Markdown、~1500 张图片。为帮助 AI 快速定位：
1. 同一知识点在不同资料中的不同叫法和覆盖深度
2. 适合插入教程的图片

**设计原则**: 纯文件索引（JSON），手动触发，无 LLM 依赖，无需额外搜索服务。

---

## 一、输出位置

```
tmp/converted/index/
├── _meta.json
├── shared_corpus.json
├── 01_尚硅谷STM32基础篇/
│   └── image_index.json
├── 04_STM32F103HAL库开发/
│   └── image_index.json
├── 嵌入式八股精华版/
│   └── image_index.json
└── 尚硅谷STM32高级篇/
    └── image_index.json
```

`index/` 目录独立于原始资料，脚本运行后自动创建。

---

## 二、共用语料索引结构

**文件**: `tmp/converted/index/shared_corpus.json`

```json
{
  "_meta": {
    "generated": "2026-04-15",
    "sources": ["01_尚硅谷STM32基础篇", "04_STM32F103HAL库开发", ...],
    "total_concepts": 180,
    "cross_material_concepts": 45
  },

  "groups": [
    {
      "topic": "GPIO",
      "variations": ["GPIO", "通用输入输出", "IO端口"],
      "cross_refs": {
        "01_尚硅谷STM32基础篇": {
          "headings": ["GPIO概述", "GPIO八种模式", "GPIO寄存器配置"],
          "keywords": ["推挽输出", "开漏输出", "浮空输入", "上拉输入", "下拉输入", "复用功能"],
          "weight": 3,
          "images": ["d2f...jpg", "7cf...jpg"]
        },
        "04_STM32F103HAL库开发": {
          "headings": ["GPIO工作原理", "HAL_GPIO函数"],
          "keywords": ["HAL_GPIO_WritePin", "HAL_GPIO_TogglePin"],
          "weight": 5,
          "images": [...]
        }
      }
    }
  ]
}
```

### 字段说明

| 字段 | 含义 |
|------|------|
| `topic` | 知识主题（归一化后的统一名称） |
| `variations` | 不同资料中的不同叫法 |
| `cross_refs` | 每个资料中该主题的对应位置 |
| `headings` | 该主题在当前资料中的相关章节标题 |
| `keywords` | 从标题和首段提取的技术术语 |
| `weight` | 覆盖权重 = 出现次数 × 层级系数（H1×3, H2×2, H3×1）|
| `images` | 与该知识点直接相关的图片 hash 列表 |

### 生成算法（无 LLM）

1. **读取所有 `full.md`**，用正则提取 `# `（H1）和 `## `（H2）标题
2. **文本归一化**：全角→半角、大写→小写、去除标点符号
3. **中文分词**：用 `jieba` 对标题分词，提取技术术语作为 `keywords`
4. **相似度匹配**：用 `python-Levenshtein`（编辑距离）比对不同资料间的标题
   - 标题文本相似度 > 60% → 认为是同一知识点的不同表述
   - 或者：标题包含关系（A 标题包含 B 标题的核心词 → 关联）
5. **分组**：将映射到同一知识点的条目归为 `group`
6. **variations**：同 group 内各资料的标题原文作为别名收集

---

## 三、图片索引结构

**文件**: 每个资料夹的 `image_index.json`

```json
{
  "_meta": {
    "source": "04_STM32F103HAL库开发",
    "total_images": 880,
    "generated": "2026-04-15"
  },

  "images": [
    {
      "filename": "de2fcdfb2a5129ed8f0022234886710648ed040cf9e0cce7262cf1cba49e9d85.jpg",
      "path": "04_STM32F103HAL库开发/images/de2fcdfb2a5129ed8f0022234886710648ed040cf9e0cce7262cf1cba49e9d85.jpg",
      "description": "ARM 内核架构图，STM32 基于 ARM 架构设计",
      "tags": ["ARM", "内核架构", "STM32概述"],
      "headings": ["1.1 关于 ARM 内核"],
      "page_approx": 3,
      "size_bytes": 45832
    }
  ]
}
```

### 字段说明

| 字段 | 含义 |
|------|------|
| `description` | 1-3句话概括图片内容（从最近标题 + 段落首句拼接，超50字截断）|
| `tags` | 从上下文的 jieba 分词中提取的技术术语 |
| `headings` | 图片所在章节的标题链 |
| `page_approx` | 从 `layout.json` bbox 信息估算的页码，找不到则为 `null` |
| `size_bytes` | 图片文件大小（字节） |

### 生成算法（无 LLM）

1. **正则匹配** `full.md` 中所有 `![](images/xxx.jpg)`
2. 取图片**前后最近一段文字**（上溯到最近换行/标题）
3. 提取该位置**最近的标题**作为描述主语
4. 取最近段落中**第一句完整句子**作为补充
5. 拼接：`{标题核心词} + {段落首句}`，超过 50 字截断
6. 用 **jieba** 对上下文分词，过滤停用词，保留名词/术语作为 `tags`
7. 从 Markdown 标题层级追溯图片所在 `headings` 链
8. 从 `layout.json` 的 bbox 信息按比例估算 `page_approx`

---

## 四、实现概要

### 脚本路径

```
scripts/indexer/
└── build_corpus_index.py
```

### 依赖

```
jieba
python-Levenshtein
```

（均通过 pip 安装，不引入额外重型依赖）

### 运行方式

```bash
py scripts/indexer/build_corpus_index.py
```

### 错误处理

- 没有 `full.md` 的资料夹 → 跳过并打印警告
- 没有 `images/` 目录 → 跳过图片索引
- 图片文件不存在 → `path` 为空字符串
- `layout.json` 不存在 → `page_approx` 为 `null`
- JSON 解析失败 → 跳过该文件并打印错误

---

## 五、使用方式

### AI 使用索引

当 AI 需要找共用知识点时：
1. 读取 `tmp/converted/index/shared_corpus.json`
2. 在 `groups` 中按 `topic` 或 `variations` 搜索
3. 找到后从 `cross_refs` 中获取各资料的具体位置

当 AI 需要找合适图片时：
1. 确定知识点关键词
2. 在对应资料夹的 `image_index.json` 中搜索 `tags`
3. 从匹配条目中取 `description` 和 `path`

### 手动更新索引

新增资料后，重新运行脚本即可：
```bash
py scripts/indexer/build_corpus_index.py
```
