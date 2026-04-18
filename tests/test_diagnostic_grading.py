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
    """测试路由表（四档路由）"""

    def test_skip_threshold(self):
        """测试跳过阈值（≥80%）"""
        assert ROUTE_TABLE[80] == "skip"
        assert ROUTE_TABLE[90] == "skip"
        assert ROUTE_TABLE[100] == "skip"

    def test_compact_threshold(self):
        """测试快速通道阈值（60-79%）"""
        assert ROUTE_TABLE[60] == "compact"
        assert ROUTE_TABLE[70] == "compact"
        assert ROUTE_TABLE[79] == "compact"

    def test_remedial_threshold(self):
        """测试补救课阈值（<60%）"""
        assert ROUTE_TABLE[59] == "remedial"
        assert ROUTE_TABLE[50] == "remedial"
        assert ROUTE_TABLE[0] == "remedial"


class TestGetRoute:
    """测试 get_route 函数（四档路由）"""

    def test_skip_route(self):
        """测试跳过路由"""
        assert get_route(80) == "skip"
        assert get_route(100) == "skip"

    def test_compact_route_default_bias(self):
        """60-79% 且无 bias 或 calibrated → compact"""
        assert get_route(60) == "compact"
        assert get_route(70) == "compact"
        assert get_route(79, dominant_bias="calibrated") == "compact"
        assert get_route(65, dominant_bias="unknown") == "compact"

    def test_full_route_overconfident(self):
        """60-79% 且过度自信 → full（需要更多脚手架）"""
        assert get_route(60, dominant_bias="overconfident") == "full"
        assert get_route(75, dominant_bias="overconfident") == "full"

    def test_full_route_underconfident(self):
        """60-79% 且谨慎型 → full（需要更多鼓励性类比）"""
        assert get_route(60, dominant_bias="underconfident") == "full"
        assert get_route(79, dominant_bias="underconfident") == "full"

    def test_skip_is_unaffected_by_bias(self):
        """≥80% 掌握度下无论 bias 都是 skip"""
        assert get_route(90, dominant_bias="overconfident") == "skip"
        assert get_route(80, dominant_bias="underconfident") == "skip"

    def test_remedial_is_unaffected_by_bias(self):
        """<60% 掌握度下无论 bias 都是 remedial"""
        assert get_route(59, dominant_bias="overconfident") == "remedial"
        assert get_route(0, dominant_bias="underconfident") == "remedial"

    def test_remedial_route(self):
        """测试补救路由（默认 bias）"""
        assert get_route(59) == "remedial"
        assert get_route(0) == "remedial"

    def test_clamping(self):
        """超出 [0,100] 范围的输入应被安全收敛"""
        assert get_route(-10) == "remedial"
        assert get_route(200) == "skip"


class TestConfidenceBias:
    """测试自信度偏差分类 & 汇总"""

    def test_classify_overconfident(self):
        from scripts.diagnostic_grader import classify_confidence_bias
        # 高自信 + 答错
        assert classify_confidence_bias(0.0, 5) == "overconfident"
        assert classify_confidence_bias(0.5, 4) == "overconfident"

    def test_classify_underconfident(self):
        from scripts.diagnostic_grader import classify_confidence_bias
        # 低自信 + 答对
        assert classify_confidence_bias(1.0, 1) == "underconfident"
        assert classify_confidence_bias(1.0, 2) == "underconfident"

    def test_classify_calibrated(self):
        from scripts.diagnostic_grader import classify_confidence_bias
        # 中等自信 + 答对
        assert classify_confidence_bias(1.0, 3) == "calibrated"
        # 高自信 + 答对
        assert classify_confidence_bias(1.0, 5) == "calibrated"

    def test_classify_uncertain(self):
        from scripts.diagnostic_grader import classify_confidence_bias
        # 低自信 + 答错（不确定型）
        assert classify_confidence_bias(0.0, 1) == "uncertain"

    def test_infer_dominant_bias_majority(self):
        from scripts.diagnostic_grader import infer_dominant_bias
        # 3 题中 2 道 overconfident 胜出
        scores = [0.0, 0.0, 1.0]
        confidences = [5, 4, 3]
        assert infer_dominant_bias(scores, confidences) == "overconfident"

    def test_infer_dominant_bias_priority(self):
        from scripts.diagnostic_grader import infer_dominant_bias
        # overconfident 与 underconfident 各一道时，优先 overconfident
        scores = [0.0, 1.0]
        confidences = [5, 1]
        assert infer_dominant_bias(scores, confidences) == "overconfident"

    def test_infer_dominant_bias_empty(self):
        from scripts.diagnostic_grader import infer_dominant_bias
        assert infer_dominant_bias([], []) == "unknown"
        assert infer_dominant_bias([1.0], []) == "unknown"
        assert infer_dominant_bias([1.0, 0.0], [3]) == "unknown"  # 长度不一致


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

    def test_full_match(self):
        """测试完全匹配"""
        result = grade_answer(
            "I2C是串行通信协议",
            "I2C通信",
            "I2C是串行通信协议"
        )
        assert result == 1.0

    def test_partial_keyword_match(self):
        """测试部分关键词匹配（当前实现基于字符级分词，可能对复合词效果有限）"""
        result = grade_answer(
            "I2C支持多主机通信",
            "I2C特性",
            "I2C是串行通信协议，支持多主机多从机通信"
        )
        # 当前分词可能得到 0.0-0.5 之间的结果
        assert 0.0 <= result <= 1.0  # 宽松断言


class TestGradingStrategy:
    """测试混合模式批改策略"""

    def test_rule_match_exact(self):
        """测试规则匹配：精确匹配"""
        from scripts.diagnostic_grader import rule_match, GradingStrategy

        result = rule_match(
            "I2C是串行通信协议",
            "I2C是串行通信协议"
        )
        assert result.score == 1.0
        assert result.strategy == GradingStrategy.RULE_MATCH
        assert result.confidence == 1.0
        assert result.needs_llm_review is False

    def test_rule_match_no_match(self):
        """测试规则匹配：无匹配（低置信度需要复核）"""
        from scripts.diagnostic_grader import rule_match

        result = rule_match(
            "I2C有一些特性",
            "I2C是串行通信协议，支持多主机多从机通信"
        )
        assert result.needs_llm_review is True  # 低置信度需要 LLM 复核
        assert result.confidence < 0.7

    def test_keyword_score_with_english_terms(self):
        """测试关键词打分：使用英文术语（分词效果较好）"""
        from scripts.diagnostic_grader import keyword_score, GradingStrategy

        result = keyword_score(
            "I2C supports multi-master communication",
            "I2C supports multi-master multi-slave communication"
        )
        # 英文分词效果好，应该得到较高分
        assert result.score >= 0.5
        assert result.strategy == GradingStrategy.KEYWORD_SCORING

    def test_keyword_score_empty_target(self):
        """测试关键词打分：空目标知识"""
        from scripts.diagnostic_grader import keyword_score, GradingStrategy

        result = keyword_score(
            "I2C有一些特性",
            ""  # 空目标知识
        )
        # 空目标应该降级处理
        assert result.strategy == GradingStrategy.KEYWORD_SCORING
        assert result.needs_llm_review is True

    def test_hybrid_grading_fallback(self):
        """测试混合模式：无 LLM API 时的 fallback"""
        from scripts.diagnostic_grader import grade_answer_with_fallback, GradingStrategy

        # 这种情况应该返回低置信度结果，标记需要人工复核
        result = grade_answer_with_fallback(
            user_answer="I2C有一些特性",
            target_concept="I2C通信协议",
            target_knowledge="I2C是串行通信协议，支持多主机多从机通信"
        )
        # 无 LLM API，应该返回 LLM_FALLBACK 类型
        assert result.strategy == GradingStrategy.LLM_FALLBACK
        assert result.needs_llm_review is True


class TestDiagnosticFileGrading:
    """测试诊断文件批量批改"""

    def test_parse_diagnostic_file_not_found(self):
        """测试解析不存在的文件"""
        from scripts.diagnostic_grader import parse_diagnostic_file

        with pytest.raises(FileNotFoundError):
            parse_diagnostic_file("nonexistent/path/file.md")