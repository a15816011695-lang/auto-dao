"""诊断批改模块"""

from typing import List, Dict

# 路由表：掌握度 -> 行动
ROUTE_TABLE: Dict[int, str] = {}

# 初始化路由表
for pct in range(0, 101):
    if pct >= 60:
        ROUTE_TABLE[pct] = "pass"
    elif pct >= 33:
        ROUTE_TABLE[pct] = "quick_review"
    else:
        ROUTE_TABLE[pct] = "remediation"


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


def grade_answer(
    user_answer: str,
    target_concept: str,
    target_knowledge: str
) -> float:
    """
    三档评估答案。
    返回: 1.0 (完全正确), 0.5 (部分正确), 0.0 (错误)

    注意：这是简化实现。实际需要 LLM 判断答案质量。

    Args:
        user_answer: 用户答案
        target_concept: 题目考察的核心概念
        target_knowledge: 期望用户掌握的知识（用于判断答偏情况）

    Returns:
        分数 1.0 / 0.5 / 0.0
    """
    if not user_answer or len(user_answer.strip()) < 2:
        return 0.0
    # 简化实现：实际需要 LLM 判断
    return 1.0


def get_route(mastery_pct: float) -> str:
    """根据掌握度返回路由行动"""
    return ROUTE_TABLE.get(int(mastery_pct), "remediation")


def grade_diagnostic_file(
    diagnostic_path: str,
    question_count: int
) -> Dict:
    """批量批改诊断文件

    Args:
        diagnostic_path: 诊断文件路径
        question_count: 诊断题数量

    Returns:
        包含掌握度、路由、详细评分的字典
    """
    scores = [1.0] * question_count  # 占位
    mastery = calculate_mastery(scores)
    route = get_route(mastery)
    return {
        "mastery_pct": mastery,
        "route": route,
        "scores": scores,
        "pass": route == "pass",
        "quick_review": route == "quick_review",
        "remediation": route == "remediation"
    }
