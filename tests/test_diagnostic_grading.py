"""Tests for scripts/diagnostic_grader.py"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.diagnostic_grader import (
    calculate_mastery,
    grade_answer,
    get_route,
    ROUTE_TABLE
)


class TestCalculateMastery:
    """测试掌握度计算"""

    def test_all_correct(self):
        """测试完全正确的情况（3题全对）"""
        scores = [1.0, 1.0, 1.0]
        mastery = calculate_mastery(scores)
        assert mastery == 100.0

    def test_two_correct_one_wrong(self):
        """测试部分正确（2对1错）"""
        scores = [1.0, 1.0, 0.0]
        mastery = calculate_mastery(scores)
        assert mastery == pytest.approx(66.7, abs=0.5)

    def test_partial_credit(self):
        """测试部分正确的情况（0.5分折算）"""
        # 1对1半对1错 = (1+0.5)/3 ≈ 50%
        scores = [1.0, 0.5, 0.0]
        mastery = calculate_mastery(scores)
        assert mastery == pytest.approx(50.0, abs=0.1)

    def test_all_wrong(self):
        """测试全部错误"""
        scores = [0.0, 0.0, 0.0]
        mastery = calculate_mastery(scores)
        assert mastery == 0.0

    def test_empty_scores(self):
        """测试空列表"""
        scores = []
        mastery = calculate_mastery(scores)
        assert mastery == 0.0


class TestRouteTable:
    """测试路由表"""

    def test_pass_threshold(self):
        """测试通过阈值（≥60%）"""
        assert ROUTE_TABLE[60] == "pass"
        assert ROUTE_TABLE[80] == "pass"
        assert ROUTE_TABLE[100] == "pass"

    def test_quick_review_threshold(self):
        """测试快速回顾阈值（33%-60%）"""
        assert ROUTE_TABLE[33] == "quick_review"
        assert ROUTE_TABLE[50] == "quick_review"
        assert ROUTE_TABLE[59] == "quick_review"

    def test_remediation_threshold(self):
        """测试补救课阈值（<33%）"""
        assert ROUTE_TABLE[0] == "remediation"
        assert ROUTE_TABLE[32] == "remediation"
        assert ROUTE_TABLE[10] == "remediation"


class TestGetRoute:
    """测试 get_route 函数"""

    def test_pass_route(self):
        """测试通过路由"""
        assert get_route(60) == "pass"
        assert get_route(100) == "pass"

    def test_quick_review_route(self):
        """测试快速回顾路由"""
        assert get_route(33) == "quick_review"
        assert get_route(50) == "quick_review"

    def test_remediation_route(self):
        """测试补救课路由"""
        assert get_route(32) == "remediation"
        assert get_route(0) == "remediation"


class TestGradeAnswer:
    """测试答案批改"""

    def test_empty_answer(self):
        """测试空答案"""
        result = grade_answer("", "时钟信号", "时钟信号用于同步数据")
        assert result == 0.0

    def test_short_answer(self):
        """测试过短的答案"""
        result = grade_answer("a", "时钟信号", "时钟信号用于同步数据")
        assert result == 0.0

    # 注意：grade_answer 的简化实现总是返回 1.0
    # 实际需要 LLM 进行真正的批改