"""前置知识缺口分析模块"""

import re
from typing import List, Set, Dict, Optional


def analyze_prerequisite_gaps(
    next_lesson_content: str,
    completed_lessons: List[str],
    prerequisite_map: Dict[str, List[str]]
) -> List[str]:
    """分析下一课的前置知识缺口

    Args:
        next_lesson_content: 下一课的讲解内容
        completed_lessons: 已完成的课程列表
        prerequisite_map: 前置知识依赖表

    Returns:
        检测到的前置知识缺口列表
    """
    gaps = set()

    # 简化实现：从下一课内容中提取关键术语
    # 实际需要 NLP 提取或使用 corpus_indexer 进行相似度匹配
    key_terms = _extract_key_terms(next_lesson_content)

    # 检查每个关键术语是否在已学课程中覆盖
    for term in key_terms:
        if not _is_covered_in_lessons(term, completed_lessons):
            gaps.add(term)

    # Merge prerequisite_map dependencies (recursive expansion)
    for term in gaps:
        if term in prerequisite_map:
            # Recursively expand dependency chain, excluding the term itself
            expanded = expand_recursive_deps(term, prerequisite_map) - {term}
            gaps.update(expanded)

    return list(gaps)


def _extract_key_terms(content: str) -> List[str]:
    """从内容中提取关键术语（简化实现）"""
    # 提取可能的前置概念关键词
    patterns = [
        r'[一-龥]+信号',  # 中文术语
        r'[A-Z][a-zA-Z]+\s*(?:信号|协议|机制|原理|基础)',
    ]
    terms = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        terms.extend(matches)
    return terms


def _is_covered_in_lessons(term: str, completed_lessons: List[str]) -> bool:
    """检查术语是否在已学课程中覆盖"""
    # 简化实现：需要更复杂的语义匹配
    for lesson in completed_lessons:
        if term in lesson:
            return True
    return False


def expand_recursive_deps(
    concept: str,
    prereq_map: Dict[str, List[str]],
    _seen: Optional[Set[str]] = None
) -> Set[str]:
    """递归展开依赖链

    Args:
        concept: 概念名称
        prereq_map: 前置知识依赖表
        _seen: 已访问的集合（内部使用）

    Returns:
        包含所有依赖的概念集合（包括输入概念本身）
    """
    if _seen is None:
        _seen = {concept}

    deps = prereq_map.get(concept, [])
    result = set(_seen)

    for dep in deps:
        if dep not in _seen:
            _seen.add(dep)
            result |= expand_recursive_deps(dep, prereq_map, _seen)

    return result
