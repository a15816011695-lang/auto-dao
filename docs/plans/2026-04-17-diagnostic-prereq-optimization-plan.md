# auto-tutor 核心脚本优化实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 diagnostic_grader.py 混合模式批改 + prereq_analyzer.py 集成 corpus_indexer

**Architecture:**
- **diagnostic_grader.py**: 采用三层批改策略 - 规则匹配(客观题) → 关键词打分(简答题) → LLM fallback(复杂题)
- **prereq_analyzer.py**: 复用 corpus_indexer 的语义匹配能力替代简单正则匹配

**Tech Stack:** Python 3.11+, jieba, Levenshtein, (可选: LLM API for fallback)

---

## 阶段一：diagnostic_grader.py 混合模式实现

### Task 1: 设计批改评分标准

**Files:**
- Modify: `scripts/diagnostic_grader.py:1-88`

**Step 1: 阅读现有实现和测试**

Run: 查看 `scripts/diagnostic_grader.py` 和 `tests/test_diagnostic_grading.py`

**Step 2: 添加批改策略类型定义**

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class GradingStrategy(Enum):
    RULE_MATCH = "rule_match"      # 规则匹配 - 客观题
    KEYWORD_SCORING = "keyword"    # 关键词打分 - 简答题
    LLM_FALLBACK = "llm"           # LLM 批改 - 复杂题

@dataclass
class GradingResult:
    score: float                  # 1.0, 0.5, 或 0.0
    strategy: GradingStrategy     # 使用的批改策略
    confidence: float             # 置信度 0-1
    reason: str                    # 批改理由
    needs_llm_review: bool        # 是否需要人工/LLM复核
```

**Step 3: Commit**

```bash
git add scripts/diagnostic_grader.py
git commit -m "feat: add grading strategy types for hybrid mode"
```

---

### Task 2: 实现规则匹配引擎

**Files:**
- Modify: `scripts/diagnostic_grader.py`

**Step 1: 编写规则匹配测试**

```python
def test_rule_match_exact_answer():
    """测试精确匹配规则"""
    result = rule_match("I2C是串行通信协议", "I2C是串行通信协议")
    assert result.score == 1.0
    assert result.strategy == GradingStrategy.RULE_MATCH

def test_rule_match_partial_keyword():
    """测试关键词部分匹配"""
    result = rule_match("I2C支持多主机", "I2C是串行通信协议，支持多主机通信")
    assert 0.5 <= result.score < 1.0
```

**Step 2: 实现规则匹配函数**

```python
def rule_match(user_answer: str, target_answer: str) -> GradingResult:
    """规则匹配：精确匹配或关键词覆盖度"""
    user_lower = user_answer.lower().strip()
    target_lower = target_answer.lower().strip()

    # 精确匹配
    if user_lower == target_lower:
        return GradingResult(
            score=1.0,
            strategy=GradingStrategy.RULE_MATCH,
            confidence=1.0,
            reason="精确匹配",
            needs_llm_review=False
        )

    # 关键词覆盖度计算
    target_keywords = extract_keywords(target_lower)
    user_keywords = extract_keywords(user_lower)
    overlap = len(target_keywords & user_keywords) / max(len(target_keywords), 1)

    if overlap >= 0.8:
        return GradingResult(
            score=1.0,
            strategy=GradingStrategy.RULE_MATCH,
            confidence=0.9,
            reason=f"关键词覆盖度 {overlap:.0%}",
            needs_llm_review=False
        )
    elif overlap >= 0.5:
        return GradingResult(
            score=0.5,
            strategy=GradingStrategy.RULE_MATCH,
            confidence=0.7,
            reason=f"关键词覆盖度 {overlap:.0%}",
            needs_llm_review=False
        )
    else:
        return GradingResult(
            score=0.0,
            strategy=GradingStrategy.RULE_MATCH,
            confidence=0.6,
            reason=f"关键词覆盖度 {overlap:.0%}",
            needs_llm_review=True  # 需要 LLM 复核
        )

def extract_keywords(text: str) -> set:
    """提取关键词（去停用词）"""
    # 复用 corpus_indexer 的分词逻辑
    from scripts.indexer.corpus_indexer import _tokenize
    return set(_tokenize(text))
```

**Step 3: 运行测试**

Run: `pytest tests/test_diagnostic_grading.py -v -k rule_match`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/diagnostic_grader.py tests/test_diagnostic_grading.py
git commit -m "feat: implement rule match engine for diagnostic grading"
```

---

### Task 3: 实现关键词打分策略

**Files:**
- Modify: `scripts/diagnostic_grader.py`

**Step 1: 编写关键词打分测试**

```python
def test_keyword_scoring_full_coverage():
    """测试关键词完全覆盖"""
    target_knowledge = "时钟信号用于同步I2C数据传输，SCL线承载时钟"
    user_answer = "时钟信号通过SCL线同步I2C数据传输"
    result = keyword_score(user_answer, target_knowledge)
    assert result.score == 1.0

def test_keyword_scoring_partial_coverage():
    """测试关键词部分覆盖"""
    target_knowledge = "时钟信号用于同步I2C数据传输，SCL线承载时钟"
    user_answer = "时钟信号用于同步数据传输"
    result = keyword_score(user_answer, target_knowledge)
    assert 0.5 <= result.score < 1.0
```

**Step 2: 实现关键词打分函数**

```python
def keyword_score(
    user_answer: str,
    target_knowledge: str,
    required_terms: Optional[list[str]] = None
) -> GradingResult:
    """
    关键词打分策略：检查答案中是否包含必要关键词和概念

    Args:
        user_answer: 用户答案
        target_knowledge: 目标知识点（期望用户掌握的内容）
        required_terms: 必要关键词列表（如果已知）

    Returns:
        GradingResult: 包含得分、策略、置信度等信息
    """
    user_lower = user_answer.lower().strip()
    target_lower = target_knowledge.lower()

    # 提取关键词
    user_kw = extract_keywords(user_lower)
    target_kw = extract_keywords(target_lower)

    # 如果指定了必要关键词，优先使用
    if required_terms:
        required_set = set(t.lower() for t in required_terms)
        user_required = user_kw & required_set
        coverage = len(user_required) / len(required_set)
    else:
        # 计算关键词覆盖率
        coverage = len(user_kw & target_kw) / max(len(target_kw), 1)

    # 得分映射
    if coverage >= 0.8:
        score = 1.0
        confidence = 0.85
    elif coverage >= 0.6:
        score = 0.75
        confidence = 0.7
    elif coverage >= 0.4:
        score = 0.5
        confidence = 0.6
    elif coverage >= 0.2:
        score = 0.25
        confidence = 0.5
    else:
        score = 0.0
        confidence = 0.4

    return GradingResult(
        score=score,
        strategy=GradingStrategy.KEYWORD_SCORING,
        confidence=confidence,
        reason=f"关键词覆盖率 {coverage:.0%}",
        needs_llm_review=(confidence < 0.7)
    )
```

**Step 3: 运行测试**

Run: `pytest tests/test_diagnostic_grading.py -v -k keyword`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/diagnostic_grader.py tests/test_diagnostic_grading.py
git commit -m "feat: implement keyword scoring strategy"
```

---

### Task 4: 实现 LLM Fallback 机制

**Files:**
- Modify: `scripts/diagnostic_grader.py`

**Step 1: 编写 LLM fallback 测试（mock）**

```python
def test_llm_fallback_triggered():
    """测试低置信度时触发 LLM fallback"""
    # 当 rule_match 和 keyword_score 置信度都低于阈值时
    result = grade_answer_with_fallback(
        user_answer="I2C有一些特性",
        target_concept="I2C通信协议",
        target_knowledge="I2C是串行通信协议，支持多主机多从机"
    )
    assert result.needs_llm_review == True
    assert result.strategy == GradingStrategy.LLM_FALLBACK
```

**Step 2: 实现 LLM fallback 函数**

```python
def grade_answer_with_fallback(
    user_answer: str,
    target_concept: str,
    target_knowledge: str,
    llm_api: Optional[callable] = None
) -> GradingResult:
    """
    混合模式批改主函数：规则匹配 → 关键词打分 → LLM fallback

    Args:
        user_answer: 用户答案
        target_concept: 题目考察的核心概念
        target_knowledge: 期望用户掌握的知识
        llm_api: LLM API 调用函数（可选，默认使用配置）

    Returns:
        GradingResult: 最终批改结果
    """
    # 策略1: 规则匹配（高置信度直接返回）
    rule_result = rule_match(user_answer, target_knowledge)
    if rule_result.confidence >= 0.9:
        return rule_result

    # 策略2: 关键词打分
    keyword_result = keyword_score(user_answer, target_knowledge)
    if keyword_result.confidence >= 0.75:
        return keyword_result

    # 策略3: LLM fallback（低置信度或需要复核）
    if llm_api:
        return llm_grade(user_answer, target_concept, target_knowledge, llm_api)

    # 无 LLM API，返回关键词打分结果但标记需要复核
    return GradingResult(
        score=keyword_result.score,
        strategy=GradingStrategy.LLM_FALLBACK,
        confidence=keyword_result.confidence * 0.5,
        reason=f"需要人工复核（置信度 {keyword_result.confidence:.0%}）",
        needs_llm_review=True
    )


def llm_grade(
    user_answer: str,
    target_concept: str,
    target_knowledge: str,
    api_func: callable
) -> GradingResult:
    """
    LLM 批改（实际使用需要配置 LLM API）

    这是一个占位实现，实际使用时可接入 Claude/GPT API
    """
    # 构造 prompt
    prompt = f"""批改以下答案：

概念: {target_concept}
期望知识: {target_knowledge}
用户答案: {user_answer}

评分标准:
- 1.0: 完全正确，核心概念和细节都正确
- 0.5: 部分正确，关键概念对但有遗漏或小错误
- 0.0: 错误，概念理解有误或遗漏关键内容

请返回 JSON 格式: {{"score": 1.0/0.5/0.0, "reason": "批改理由"}}
"""

    try:
        response = api_func(prompt)
        import json
        result = json.loads(response)
        return GradingResult(
            score=float(result["score"]),
            strategy=GradingStrategy.LLM_FALLBACK,
            confidence=0.85,
            reason=result.get("reason", ""),
            needs_llm_review=False
        )
    except Exception as e:
        # LLM 调用失败，降级到保守评分
        return GradingResult(
            score=0.5,
            strategy=GradingStrategy.LLM_FALLBACK,
            confidence=0.3,
            reason=f"LLM调用失败，使用保守评分: {str(e)}",
            needs_llm_review=True
        )
```

**Step 3: 更新 grade_answer 入口函数**

```python
def grade_answer(
    user_answer: str,
    target_concept: str,
    target_knowledge: str
) -> float:
    """
    三档评估答案（混合模式入口函数）
    返回: 1.0 (完全正确), 0.5 (部分正确), 0.0 (错误)

    内部使用规则匹配 + 关键词打分 + LLM fallback
    """
    result = grade_answer_with_fallback(
        user_answer=user_answer,
        target_concept=target_concept,
        target_knowledge=target_knowledge
    )
    return result.score
```

**Step 4: 运行测试**

Run: `pytest tests/test_diagnostic_grading.py -v`
Expected: PASS (排除需要 llm_api 的测试)

**Step 5: Commit**

```bash
git add scripts/diagnostic_grader.py tests/test_diagnostic_grading.py
git commit -m "feat: implement LLM fallback and hybrid grading entry point"
```

---

### Task 5: 更新 grade_diagnostic_file 支持混合模式

**Files:**
- Modify: `scripts/diagnostic_grader.py`

**Step 1: 添加诊断题解析函数**

```python
def parse_diagnostic_file(diagnostic_path: str) -> list[dict]:
    """
    解析诊断文件，提取题目和期望答案

    格式: 诊断文件包含多个 ### 题目N 区域
    每个区域有: 题目描述、target_concept、target_knowledge

    Returns:
        list[dict]: [{"question": str, "target_concept": str, "target_knowledge": str}, ...]
    """
    from pathlib import Path

    path = Path(diagnostic_path)
    if not path.exists():
        raise FileNotFoundError(f"诊断文件不存在: {diagnostic_path}")

    content = path.read_text(encoding="utf-8")

    # 简单的题目解析（基于模板格式）
    # TODO: 后续可使用更健壮的 Markdown 解析
    questions = []
    blocks = content.split("### 题目")

    for block in blocks[1:]:  # 跳过标题
        lines = block.strip().split("\n")
        question_text = lines[0].strip()

        # 提取 target_concept 和 target_knowledge（如果存在）
        target_concept = ""
        target_knowledge = ""

        for line in lines[1:]:
            if line.startswith("**考察概念**:"):
                target_concept = line.split(":", 1)[1].strip()
            elif line.startswith("**期望知识**:"):
                target_knowledge = line.split(":", 1)[1].strip()

        questions.append({
            "question": question_text,
            "target_concept": target_concept,
            "target_knowledge": target_knowledge
        })

    return questions


def grade_diagnostic_file(
    diagnostic_path: str,
    question_count: int = None,
    user_answers: list[str] = None
) -> Dict:
    """
    批量批改诊断文件（支持混合模式）

    Args:
        diagnostic_path: 诊断文件路径
        question_count: 诊断题数量（可选，从文件解析）
        user_answers: 用户答案列表（可选，从文件解析）

    Returns:
        包含掌握度、路由、详细评分的字典
    """
    # 解析诊断文件
    questions = parse_diagnostic_file(diagnostic_path)
    actual_count = len(questions)

    if question_count is None:
        question_count = actual_count
    if user_answers is None:
        user_answers = ["" for _ in range(question_count)]

    # 逐题批改
    scores = []
    results = []

    for i, q in enumerate(questions):
        if i < len(user_answers):
            user_answer = user_answers[i]
        else:
            user_answer = ""

        result = grade_answer_with_fallback(
            user_answer=user_answer,
            target_concept=q.get("target_concept", ""),
            target_knowledge=q.get("target_knowledge", "")
        )
        scores.append(result.score)
        results.append(result)

    mastery = calculate_mastery(scores)
    route = get_route(mastery)

    # 检查是否需要人工复核
    needs_review = any(r.needs_llm_review for r in results)

    return {
        "mastery_pct": mastery,
        "route": route,
        "scores": scores,
        "results": [
            {"score": r.score, "strategy": r.strategy.value, "reason": r.reason}
            for r in results
        ],
        "needs_review": needs_review,
        "pass": route == "pass",
        "quick_review": route == "quick_review",
        "remediation": route == "remediation"
    }
```

**Step 2: 更新路由表（四档路由）**

```python
# 更新 ROUTE_TABLE 支持新路由
ROUTE_TABLE: Dict[int, str] = {}

for pct in range(0, 101):
    if pct >= 80:
        ROUTE_TABLE[pct] = "skip"      # Skip: ≥80%
    elif pct >= 60:
        ROUTE_TABLE[pct] = "compact"   # Compact: 60-79%
    else:
        ROUTE_TABLE[pct] = "remedial"  # Remedial: <60%


def get_route(mastery_pct: float) -> str:
    """根据掌握度返回四档路由"""
    return ROUTE_TABLE.get(int(mastery_pct), "remedial")
```

**Step 3: 运行测试**

Run: `pytest tests/test_diagnostic_grading.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/diagnostic_grader.py tests/test_diagnostic_grading.py
git commit -m "feat: update grade_diagnostic_file with hybrid mode and four-tier routing"
```

---

## 阶段二：prereq_analyzer.py 集成 corpus_indexer

### Task 6: 设计 indexer 集成方案

**Files:**
- Modify: `scripts/prereq_analyzer.py`

**Step 1: 编写 indexer 集成设计注释**

在 `prereq_analyzer.py` 头部添加设计说明：

```python
"""
前置知识缺口分析模块

设计: 集成 corpus_indexer 实现语义级前置依赖检测

集成策略:
1. 用 corpus_indexer 构建已完成课程的知识索引
2. 新课内容作为查询，在索引中检索相关概念
3. 未检索到的概念判定为潜在前置缺口
4. 结合 prerequisite_map 进行递归依赖展开

依赖:
- scripts/indexer/corpus_indexer.py
- scripts/indexer.md_parser (Heading)
- scripts.indexer.utils (read_text_safe, extract_folder_label)
"""
```

**Step 2: Commit**

```bash
git add scripts/prereq_analyzer.py
git commit -m "docs: add indexer integration design notes to prereq_analyzer"
```

---

### Task 7: 实现基于 indexer 的语义匹配

**Files:**
- Modify: `scripts/prereq_analyzer.py`

**Step 1: 编写 indexer 集成测试**

```python
def test_indexer_based_coverage_check():
    """测试基于 indexer 的课程覆盖检测"""
    # 准备模拟数据
    completed_folders = [Path("materials/i2c_lesson")]
    next_lesson_text = "SPI协议的时钟信号用于同步数据传输"

    result = is_covered_by_indexer(
        concept="时钟信号",
        completed_folders=completed_folders
    )
    # 根据实际材料内容返回 True 或 False
    assert isinstance(result, bool)
```

**Step 2: 实现基于 indexer 的覆盖检测**

```python
def is_covered_by_indexer(
    concept: str,
    completed_folders: list[Path],
    sim_threshold: float = 0.5
) -> bool:
    """
    使用 corpus_indexer 检查概念是否在已完成课程中覆盖

    Args:
        concept: 待检测概念（如"时钟信号"）
        completed_folders: 已完成课程的文件夹列表
        sim_threshold: 相似度阈值

    Returns:
        True 如果找到高相似度匹配，否则 False
    """
    from indexer.corpus_indexer import (
        build_material_entries,
        _compute_similarity,
        _tokenize
    )

    if not completed_folders:
        return False

    # 构建已完成课程的索引
    entries = build_material_entries(completed_folders)

    # 提取概念的关键词
    concept_kw = set(_tokenize(concept))

    # 在每个课程中搜索相关概念
    for entry in entries:
        for heading in entry.headings:
            heading_kw = set(entry.keywords_per_heading.get(heading.text, []))

            # 关键词重叠度
            kw_overlap = len(concept_kw & heading_kw) / max(len(concept_kw | heading_kw), 1)

            # 文本相似度
            text_sim = _compute_similarity(concept, heading.text)

            # 任一指标超过阈值即视为覆盖
            if kw_overlap >= sim_threshold or text_sim >= sim_threshold * 1.5:
                return True

    return False
```

**Step 3: 运行测试**

Run: `pytest tests/test_prereq_analysis.py -v -k indexer`
Expected: 导入错误（需要先调整 PYTHONPATH 或在项目根目录运行）

**Step 4: Commit**

```bash
git add scripts/prereq_analyzer.py tests/test_prereq_analysis.py
git commit -m "feat: implement indexer-based concept coverage detection"
```

---

### Task 8: 重构 analyze_prerequisite_gaps 使用 indexer

**Files:**
- Modify: `scripts/prereq_analyzer.py`

**Step 1: 编写重构后的 analyze_prerequisite_gaps 测试**

```python
def test_analyze_prerequisite_gaps_with_indexer():
    """测试集成 indexer 后的前置缺口分析"""
    gaps = analyze_prerequisite_gaps(
        next_lesson_content="SPI CPOL定义了时钟空闲时的电平状态",
        completed_lessons=["materials/i2c_lesson", "materials/uart_lesson"],
        prerequisite_map={"SPI CPOL": ["时钟信号"]}
    )
    # 应该正确检测到前置缺口
    assert isinstance(gaps, list)
```

**Step 2: 重构 analyze_prerequisite_gaps 函数**

```python
def analyze_prerequisite_gaps(
    next_lesson_content: str,
    completed_lessons: list[str],
    prerequisite_map: dict[str, list[str]],
    use_indexer: bool = True
) -> list[str]:
    """
    分析下一课的前置知识缺口

    Args:
        next_lesson_content: 下一课的讲解内容
        completed_lessons: 已完成的课程文件夹路径列表
        prerequisite_map: 前置知识依赖表（概念 -> 前置概念列表）
        use_indexer: 是否使用 corpus_indexer（默认 True）

    Returns:
        检测到的前置知识缺口列表
    """
    from pathlib import Path

    gaps = set()

    # 策略1: 使用 prerequisite_map 直接检测
    # 从新课内容中提取可能的概念（使用 indexer 的分词）
    content_terms = _extract_concepts(next_lesson_content)

    # 检查 prerequisite_map 中的前置依赖
    for term in content_terms:
        if term in prerequisite_map:
            for prereq in prerequisite_map[term]:
                gaps.add(prereq)

    # 策略2: 使用 indexer 语义匹配（如果启用）
    if use_indexer and completed_lessons:
        completed_paths = [Path(p) if isinstance(p, str) else p for p in completed_lessons]

        for term in content_terms:
            if not is_covered_by_indexer(term, completed_paths):
                # 概念未被已学课程覆盖，添加到缺口
                gaps.add(term)

    # 递归展开依赖链（使用 prerequisite_map）
    expanded_gaps = set()
    for gap in gaps:
        expanded = expand_recursive_deps(gap, prerequisite_map)
        expanded_gaps |= expanded

    return list(expanded_gaps - gaps) + list(gaps)


def _extract_concepts(content: str) -> list[str]:
    """从内容中提取关键概念（使用 indexer 分词增强）"""
    from indexer.corpus_indexer import _tokenize

    # 使用 jieba 分词提取关键词
    tokens = _tokenize(content)

    # 过滤太短的词和停用词
    significant_tokens = [t for t in tokens if len(t) >= 2]

    return significant_tokens
```

**Step 3: 运行完整测试**

Run: `pytest tests/test_prereq_analysis.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/prereq_analyzer.py tests/test_prereq_analysis.py
git commit -m "refactor: integrate corpus_indexer for semantic prerequisite detection"
```

---

### Task 9: 添加 indexer 导入兼容性处理

**Files:**
- Modify: `scripts/prereq_analyzer.py`

**Step 1: 添加导入兼容性代码**

```python
# 尝试导入 indexer 模块（可选依赖）
try:
    from indexer.corpus_indexer import build_material_entries, _compute_similarity, _tokenize
    from indexer.md_parser import extract_headings
    from indexer.utils import read_text_safe, extract_folder_label
    INDEXER_AVAILABLE = True
except ImportError:
    INDEXER_AVAILABLE = False
    _tokenize = None  # type: ignore
```

**Step 2: 更新 is_covered_by_indexer 处理无 indexer 情况**

```python
def is_covered_by_indexer(...):
    if not INDEXER_AVAILABLE:
        # 降级到简单的字符串包含检查
        return _simple_string_contains(concept, completed_lessons)
    ...
```

**Step 3: Commit**

```bash
git add scripts/prereq_analyzer.py
git commit -m "chore: add indexer import fallback for compatibility"
```

---

## 验收测试

### 运行完整测试套件

Run: `pytest tests/test_diagnostic_grading.py tests/test_prereq_analysis.py -v --tb=short`

Expected Results:
- `test_rule_match_*`: PASS
- `test_keyword_scoring_*`: PASS
- `test_llm_fallback_*`: PASS (mocked)
- `test_indexer_based_*`: PASS
- `test_analyze_prerequisite_gaps_*`: PASS

### 集成测试

Run: 手动测试完整流程
1. 生成一个诊断文件
2. 运行 `grade_diagnostic_file()` 验证批改
3. 运行 `analyze_prerequisite_gaps()` 验证前置检测

---

## 后续优化项（不包含在当前计划中）

| 优先级 | 优化项 | 说明 |
|--------|--------|------|
| P1 | comprehensive-assessment 集成 | 将独立 skill 集成到主管线 |
| P1 | lesson-template.md 精简 | 消除"知识导航"和"知识回引"的冗余 |
| P2 | 间隔复习触发机制 | 实现 Spaced Repetition 调度 |
| P2 | Schema 版本一致性 | 将 session-state.schema.json 升级到 v2.1 |

---

*计划生成时间: 2026-04-17*
*对应设计文档: docs/superpowers/specs/2026-04-16-adaptive-learning-upgrade-design.md*
