"""诊断批改模块 — 混合模式实现

批改策略（优先级从高到低）：
1. 规则匹配（rule_match）：精确匹配或关键词完全覆盖 → 高置信度直接返回
2. 关键词打分（keyword_score）：部分关键词覆盖 → 中置信度
3. LLM fallback（llm_fallback）：低置信度或答偏检测 → 需要人工/LLM复核

四档路由（对应 SKILL.md Step 3.5.5）：
- skip:     mastery ≥ 80%                                           → 可压缩讲解
- compact:  60-79% 且 校准良好（calibrated）                         → 快速回顾薄弱点
- full:     60-79% 且 过度自信/谨慎型（overconfident/underconfident） → 完整讲解 + 额外 Worked Example
- remedial: mastery < 60%                                            → 前置补救课
"""

from enum import Enum
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

class GradingStrategy(Enum):
    RULE_MATCH = "rule_match"      # 规则匹配 - 精确或高覆盖
    KEYWORD_SCORING = "keyword"    # 关键词打分 - 部分覆盖
    LLM_FALLBACK = "llm"           # LLM 批改 - 复杂题
    UNKNOWN = "unknown"            # 未知（未评分）


@dataclass
class GradingResult:
    """单个答案的批改结果"""
    score: float                  # 1.0, 0.5, 或 0.0
    strategy: GradingStrategy     # 使用的批改策略
    confidence: float             # 置信度 0-1
    reason: str                   # 批改理由
    needs_llm_review: bool       # 是否需要人工/LLM复核


# 路由表：掌握度 -> 行动（三档基础路由，不考虑 confidence_bias）
# 完整四档路由需要使用 get_route(mastery_pct, dominant_bias=...)
ROUTE_TABLE: Dict[int, str] = {}

# 初始化路由表
for pct in range(0, 101):
    if pct >= 80:
        ROUTE_TABLE[pct] = "skip"      # Skip: ≥80%
    elif pct >= 60:
        ROUTE_TABLE[pct] = "compact"   # Compact: 60-79%（默认校准良好）
    else:
        ROUTE_TABLE[pct] = "remedial"  # Remedial: <60%


# confidence_bias 值 → 是否触发 Full 路由
# SKILL.md Step 3.5.5：过度自信 + 谨慎型都会在 60-79% 区间升级到 Full
FULL_ROUTE_BIASES = {"overconfident", "underconfident"}


def calculate_mastery(scores: List[float]) -> float:
    """计算掌握度：(完全正确×1.0 + 部分正确×0.5) / 总题数 × 100

    Args:
        scores: 每题得分列表，每项为 1.0（完全正确）、0.5（部分正确）或 0.0（错误）

    Returns:
        掌握度百分比（0-100）
    """
    count = len(scores)
    if count == 0:
        return 0.0
    total = sum(scores)
    return (total / count) * 100


def _tokenize(text: str) -> set:
    """简单的中文分词（去停用词）"""
    import re
    # 停用词
    STOPWORDS = {"的", "是", "在", "了", "和", "与", "或", "以及", "为", "其",
                 "本", "该", "各", "个", "等", "之", "以", "于", "对", "中", "上",
                 "下", "可", "能", "将", "要", "会", "有", "从", "到", "也", "而",
                 "又", "但", "则", "所", "被", "比", "如", "当", "由", "此", "并"}

    # 提取中文词和英文词
    tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text.lower())
    return {t for t in tokens if len(t) >= 2 and t not in STOPWORDS}


def extract_keywords(text: str) -> set:
    """提取关键词（去停用词）"""
    return _tokenize(text)


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

    if not target_keywords:
        # 目标答案没有可提取的关键词，降级处理
        return GradingResult(
            score=0.5,
            strategy=GradingStrategy.RULE_MATCH,
            confidence=0.5,
            reason="目标答案无法分析关键词",
            needs_llm_review=True
        )

    overlap = len(target_keywords & user_keywords) / len(target_keywords)

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
            needs_llm_review=True
        )


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
        if not target_kw:
            return GradingResult(
                score=0.5,
                strategy=GradingStrategy.KEYWORD_SCORING,
                confidence=0.4,
                reason="目标知识无法提取关键词",
                needs_llm_review=True
            )
        coverage = len(user_kw & target_kw) / len(target_kw)

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


def grade_answer_with_fallback(
    user_answer: str,
    target_concept: str,
    target_knowledge: str,
    llm_api: Optional[Callable[[str], str]] = None,
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
    # 空答案或过短答案
    if not user_answer or len(user_answer.strip()) < 2:
        return GradingResult(
            score=0.0,
            strategy=GradingStrategy.UNKNOWN,
            confidence=1.0,
            reason="答案为空或过短",
            needs_llm_review=False
        )

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
        return _llm_grade(user_answer, target_concept, target_knowledge, llm_api)

    # 无 LLM API，返回关键词打分结果但标记需要复核
    return GradingResult(
        score=keyword_result.score,
        strategy=GradingStrategy.LLM_FALLBACK,
        confidence=keyword_result.confidence * 0.5,
        reason=f"需要人工复核（置信度 {keyword_result.confidence:.0%}）",
        needs_llm_review=True
    )


def _llm_grade(
    user_answer: str,
    target_concept: str,
    target_knowledge: str,
    api_func: Callable[[str], str],
) -> GradingResult:
    """
    LLM 批改（实际使用需要配置 LLM API）

    这是一个占位实现，实际使用时可接入 Claude/GPT API
    """
    import json

    # 构造 prompt
    prompt = f"""批改以下诊断答案：

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


def get_route(mastery_pct: float, dominant_bias: Optional[str] = None) -> str:
    """根据掌握度和主导自信度偏差返回四档路由（SKILL.md Step 3.5.5）。

    Args:
        mastery_pct: 综合掌握度百分比 (0-100)。
        dominant_bias: 本轮诊断中主导的 confidence_bias 模式；取值应与
            session_state.learner_model.overall_confidence_bias 的枚举保持一致：
            ``"calibrated"`` / ``"overconfident"`` / ``"underconfident"`` / ``"unknown"``。
            为 ``None`` 或 ``"calibrated"`` 时走基础三档；若为过度自信或谨慎型则在
            60-79% 区间升级到 ``"full"``。

    Returns:
        ``"skip"``、``"compact"``、``"full"`` 或 ``"remedial"`` 之一。
    """
    # 输入规范化：负值或超过 100 的值向内收敛
    pct = max(0, min(100, int(mastery_pct)))
    base = ROUTE_TABLE.get(pct, "remedial")
    # 仅当处于 compact 区间且自信度偏差属于 overconfident/underconfident 时升级到 full
    if base == "compact" and dominant_bias in FULL_ROUTE_BIASES:
        return "full"
    return base


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
    questions = []
    blocks = content.split("### 题目")

    for block in blocks[1:]:  # 跳过标题
        lines = block.strip().split("\n")
        question_text = lines[0].strip()

        # 提取 target_concept 和 target_knowledge（如果存在）
        target_concept = ""
        target_knowledge = ""

        for line in lines[1:]:
            if "**考察概念**:" in line:
                target_concept = line.split(":", 1)[1].strip().strip("*")
            elif "**期望知识**:" in line:
                target_knowledge = line.split(":", 1)[1].strip().strip("*")

        questions.append({
            "question": question_text,
            "target_concept": target_concept,
            "target_knowledge": target_knowledge
        })

    return questions


def grade_diagnostic_file(
    diagnostic_path: str,
    question_count: Optional[int] = None,
    user_answers: Optional[List[str]] = None,
    dominant_bias: Optional[str] = None,
    confidences: Optional[List[int]] = None,
) -> Dict:
    """
    批量批改诊断文件（支持混合模式 + 四档路由）。

    Args:
        diagnostic_path: 诊断文件路径
        question_count: 诊断题数量（可选，从文件解析）
        user_answers: 用户答案列表（可选，从文件解析）
        dominant_bias: 主导 confidence_bias（计算后传入 get_route）；
            若为 ``None`` 且 ``confidences`` 非空，则自动由得分+自信度推断。
        confidences: 每题 self-reported 自信度 1-5；若提供，则根据
            SKILL.md Step 3.5.5 的四种偏移类别推断 dominant_bias。

    Returns:
        包含掌握度、路由、详细评分的字典
    """
    # 解析诊断文件
    questions = parse_diagnostic_file(diagnostic_path)
    actual_count = len(questions)

    if question_count is None:
        question_count = actual_count
    if user_answers is None:
        # 尝试从文件中提取答案（格式: "**我的答案**：xxx"）
        user_answers = _extract_answers_from_file(diagnostic_path, actual_count)

    # 逐题批改
    scores = []
    results = []

    for i, q in enumerate(questions):
        if i < len(user_answers):
            user_answer = user_answers[i] if user_answers[i] else ""
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

    # 若调用方没传入 dominant_bias 但提供了 confidences，则从 (score, confidence) 对推断
    inferred_bias = dominant_bias
    if inferred_bias is None and confidences:
        inferred_bias = infer_dominant_bias(scores, confidences)

    route = get_route(mastery, dominant_bias=inferred_bias)

    # 检查是否需要人工复核
    needs_review = any(r.needs_llm_review for r in results)

    return {
        "mastery_pct": mastery,
        "route": route,
        "scores": scores,
        "dominant_bias": inferred_bias,
        "results": [
            {"score": r.score, "strategy": r.strategy.value, "reason": r.reason}
            for r in results
        ],
        "needs_review": needs_review,
        "skip": route == "skip",
        "compact": route == "compact",
        "full": route == "full",
        "remedial": route == "remedial",
    }


def classify_confidence_bias(score: float, confidence: int) -> str:
    """给单道题分类 confidence_bias（SKILL.md Step 3.5.5）。

    Args:
        score: 答题得分 1.0/0.5/0.0。
        confidence: 用户作答前自评 1-5。

    Returns:
        ``"overconfident"`` / ``"calibrated"`` / ``"underconfident"`` / ``"uncertain"``。
        ``uncertain`` 对应"低自信 + 错" — 未转嫁到 learner_model 偏差，视为校准但需关注。
    """
    high_conf = confidence >= 4
    low_conf = confidence <= 2
    correct = score >= 1.0  # 只有完全正确记作掌握
    partial_or_wrong = score < 1.0
    if high_conf and partial_or_wrong:
        return "overconfident"
    if low_conf and correct:
        return "underconfident"
    if low_conf and partial_or_wrong:
        return "uncertain"
    return "calibrated"


def infer_dominant_bias(scores: List[float], confidences: List[int]) -> str:
    """汇总每题偏差，取"众数"为主导 bias（过度自信/谨慎型优先于校准）。

    若 overconfident 与 underconfident 并列，取 overconfident（更紧急——需更多脚手架）。
    若样本不足（长度不一致或 confidences 全空）则返回 ``"unknown"``。
    """
    if not scores or not confidences or len(scores) != len(confidences):
        return "unknown"
    counts: Dict[str, int] = {}
    for s, c in zip(scores, confidences):
        bias = classify_confidence_bias(s, c)
        counts[bias] = counts.get(bias, 0) + 1
    # 优先级：overconfident > underconfident > uncertain > calibrated
    priority = ["overconfident", "underconfident", "uncertain", "calibrated"]
    # 取出现次数最多的 bias；同频次按优先级打破平手
    max_count = max(counts.values()) if counts else 0
    for bias in priority:
        if counts.get(bias, 0) == max_count and max_count > 0:
            return bias
    return "unknown"


def _extract_answers_from_file(diagnostic_path: str, expected_count: int) -> list:
    """从诊断文件中提取用户答案"""
    from pathlib import Path

    try:
        content = Path(diagnostic_path).read_text(encoding="utf-8")
    except Exception:
        return [""] * expected_count

    answers = []
    # 匹配 "**我的答案**：" 后面的内容到下一个 "---" 或空行
    import re
    pattern = r"\*\*我的答案\*\*[：:]\s*\n(.*?)(?=---|\n###|\n##|$)"
    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        # 清理答案文本
        answer = match.strip()
        # 取第一段（去除引用块等）
        answer = answer.split("\n>")[0].strip()
        answers.append(answer)

    # 如果没有匹配到，返回空列表
    if not answers:
        return [""] * expected_count

    return answers
