"""前置知识缺口分析模块

设计: 集成 corpus_indexer 实现语义级前置依赖检测

集成策略:
1. 用 corpus_indexer 构建已完成课程的知识索引
2. 新课内容作为查询，在索引中检索相关概念
3. 未检索到的概念判定为潜在前置缺口
4. 结合 prerequisite_map 进行递归依赖展开

依赖:
- scripts/indexer/corpus_indexer.py (可选)
- 如果 indexer 不可用，降级到简单的字符串匹配
"""

import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

# 尝试导入 indexer 模块（可选依赖）
indexer_tokenize: Optional[Callable[[str], List[str]]]
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from indexer.corpus_indexer import (
        build_material_entries,
        _compute_similarity,
        _tokenize as indexer_tokenize,
    )
    INDEXER_AVAILABLE = True
except ImportError:
    INDEXER_AVAILABLE = False
    indexer_tokenize = None


def analyze_prerequisite_gaps(
    next_lesson_content: str,
    completed_lessons: List[str],
    prerequisite_map: Dict[str, List[str]],
    use_indexer: bool = True
) -> List[str]:
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
    gaps = set()

    # 策略1: 使用 prerequisite_map 直接检测
    # 从新课内容中提取可能的概念
    content_terms = _extract_concepts(next_lesson_content)

    # 检查 prerequisite_map 中的前置依赖
    for term in content_terms:
        if term in prerequisite_map:
            for prereq in prerequisite_map[term]:
                gaps.add(prereq)

    # 策略2: 使用 indexer 语义匹配（如果启用）
    if use_indexer and completed_lessons and INDEXER_AVAILABLE:
        completed_paths = [Path(p) if isinstance(p, str) else p for p in completed_lessons]

        for term in content_terms:
            if not is_covered_by_indexer(term, completed_paths):
                # 概念未被已学课程覆盖，添加到缺口
                gaps.add(term)
    elif use_indexer and completed_lessons:
        # 降级到简单的字符串匹配
        for term in content_terms:
            if not _is_covered_in_lessons(term, completed_lessons):
                gaps.add(term)

    # 递归展开依赖链（使用 prerequisite_map）
    expanded_gaps = set()
    for gap in gaps:
        expanded = expand_recursive_deps(gap, prerequisite_map)
        expanded_gaps |= expanded

    return list(expanded_gaps - gaps) + list(gaps)


def _extract_concepts(content: str) -> List[str]:
    """从内容中提取关键概念（增强版）"""
    # 如果 indexer 可用，使用其分词能力
    if INDEXER_AVAILABLE and indexer_tokenize:
        tokens = indexer_tokenize(content)
        # 过滤太短的词和停用词
        significant_tokens = [t for t in tokens if len(t) >= 2]
        return significant_tokens

    # 降级实现：使用正则提取
    patterns = [
        r'[一-龥]+信号',  # 中文术语
        r'[A-Z][a-zA-Z]+\s*(?:信号|协议|机制|原理|基础)',
        r'[\u4e00-\u9fff]{3,}',  # 3个以上连续汉字
    ]
    terms = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        terms.extend(matches)

    # 去重
    return list(set(terms))


def is_covered_by_indexer(
    concept: str,
    completed_folders: List[Path],
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
    if not INDEXER_AVAILABLE or not completed_folders:
        return False

    try:
        # 构建已完成课程的索引
        valid_folders = [f for f in completed_folders if f.exists() and f.is_dir()]
        if not valid_folders:
            return False

        entries = build_material_entries(valid_folders)

        # 提取概念的关键词
        concept_kw = set(indexer_tokenize(concept)) if indexer_tokenize else set()

        # 在每个课程中搜索相关概念
        for entry in entries:
            for heading in entry.headings:
                heading_kw = set(entry.keywords_per_heading.get(heading.text, []))

                # 关键词重叠度
                if concept_kw and heading_kw:
                    kw_overlap = len(concept_kw & heading_kw) / max(len(concept_kw | heading_kw), 1)
                else:
                    kw_overlap = 0.0

                # 文本相似度
                text_sim = _compute_similarity(concept, heading.text)

                # 任一指标超过阈值即视为覆盖
                if kw_overlap >= sim_threshold or text_sim >= sim_threshold * 1.5:
                    return True

        return False

    except Exception:
        # 出错时降级
        return False


def _is_covered_in_lessons(term: str, completed_lessons: List[str]) -> bool:
    """检查术语是否在已学课程中覆盖（降级实现）"""
    for lesson in completed_lessons:
        lesson_path = Path(lesson) if isinstance(lesson, str) else lesson

        # 检查是否是文件名
        if term in str(lesson_path.name):
            return True

        # 如果是文件夹，检查是否包含相关文件
        if lesson_path.is_dir():
            try:
                # 尝试读取 full.md 或 index.md
                for candidate in ["full.md", "index.md"]:
                    file_path = lesson_path / candidate
                    if file_path.exists():
                        content = file_path.read_text(encoding="utf-8")
                        if term in content:
                            return True
            except Exception:
                continue

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
