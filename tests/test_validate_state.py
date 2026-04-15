"""Tests for scripts/session/validate_state.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.session.validate_state import (
    check_schema_version,
    check_required_fields,
    check_phase,
    check_counterfactual_mode,
    check_wait_reason,
    check_lesson_count,
    check_lesson_continuity,
    check_completed_has_report,
    check_mastery_rate,
    check_learning_has_lesson,
    VALID_PHASES,
    VALID_CF_MODES,
    VALID_WAIT_REASONS,
)


class TestCheckSchemaVersion:
    def test_valid(self):
        state = {"schema_version": "2.0"}
        result = check_schema_version(state)
        assert result.passed

    def test_invalid(self):
        state = {"schema_version": "1.0"}
        result = check_schema_version(state)
        assert not result.passed

    def test_missing(self):
        state = {}
        result = check_schema_version(state)
        assert not result.passed


class TestCheckRequiredFields:
    def test_all_present(self):
        state = {
            "schema_version": "2.0",
            "topic_id": "test",
            "source_path": "test.pdf",
            "phase": "learning",
            "current_lesson": 1,
            "total_lessons": 5,
            "created_at": "2026-01-01T00:00:00+08:00",
            "updated_at": "2026-01-01T00:00:00+08:00",
        }
        result = check_required_fields(state)
        assert result.passed

    def test_missing_fields(self):
        state = {"schema_version": "2.0", "topic_id": "test"}
        result = check_required_fields(state)
        assert not result.passed
        assert len(result.detail) > 0


class TestCheckPhase:
    def test_valid_phases(self):
        for phase in VALID_PHASES:
            result = check_phase({"phase": phase})
            assert result.passed, f"phase '{phase}' should be valid"

    def test_invalid_phase(self):
        result = check_phase({"phase": "invalid"})
        assert not result.passed

    def test_missing_phase(self):
        result = check_phase({})
        assert not result.passed


class TestCheckCounterfactualMode:
    def test_valid_modes(self):
        for mode in VALID_CF_MODES:
            result = check_counterfactual_mode({"counterfactual_mode": mode})
            assert result.passed, f"mode '{mode}' should be valid"

    def test_invalid_mode(self):
        result = check_counterfactual_mode({"counterfactual_mode": "yes"})
        assert not result.passed


class TestCheckWaitReason:
    def test_valid_reasons(self):
        for reason in VALID_WAIT_REASONS:
            result = check_wait_reason({"wait_reason": reason})
            assert result.passed, f"reason '{reason}' should be valid"

    def test_invalid_reason(self):
        result = check_wait_reason({"wait_reason": "invalid"})
        assert not result.passed


class TestCheckLessonContinuity:
    def test_empty_dir(self, tmp_path: Path):
        result = check_lesson_continuity(tmp_path)
        assert result.passed

    def test_no_lesson_files(self, tmp_path: Path):
        # Create a non-lesson file
        (tmp_path / "summary.md").touch()
        result = check_lesson_continuity(tmp_path)
        assert result.passed  # No lesson files means trivially continuous

    def test_consecutive_lessons(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_2.md").touch()
        (tmp_path / "lesson_3.md").touch()
        result = check_lesson_continuity(tmp_path)
        assert result.passed

    def test_missing_lesson(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_3.md").touch()  # Missing lesson_2
        result = check_lesson_continuity(tmp_path)
        assert not result.passed


class TestCheckLessonCount:
    def test_current_matches_max(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_2.md").touch()
        state = {"current_lesson": 2}
        result = check_lesson_count(state, tmp_path)
        assert result.passed

    def test_current_is_next_to_generate(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"current_lesson": 2}
        result = check_lesson_count(state, tmp_path)
        assert result.passed  # current=2 means next to generate, max file is 1

    def test_no_lessons_dir_current_zero(self, tmp_path: Path):
        state = {"current_lesson": 0}
        result = check_lesson_count(state, tmp_path)
        assert result.passed

    def test_no_lessons_dir_current_nonzero(self, tmp_path: Path):
        state = {"current_lesson": 3}
        result = check_lesson_count(state, tmp_path)
        assert not result.passed


class TestCheckMasteryRate:
    def test_no_attempts_zero_rate(self):
        state = {"mastery_passed": 0, "mastery_failed": 0, "mastery_rate": 0.0}
        result = check_mastery_rate(state)
        assert result.passed

    def test_no_attempts_nonzero_rate(self):
        state = {"mastery_passed": 0, "mastery_failed": 0, "mastery_rate": 0.5}
        result = check_mastery_rate(state)
        assert not result.passed

    def test_correct_rate(self):
        state = {"mastery_passed": 6, "mastery_failed": 1, "mastery_rate": 0.857}
        result = check_mastery_rate(state)
        assert result.passed

    def test_incorrect_rate(self):
        state = {"mastery_passed": 5, "mastery_failed": 5, "mastery_rate": 0.3}
        result = check_mastery_rate(state)
        assert not result.passed


class TestCheckCompletedHasReport:
    def test_phase_not_completed(self, tmp_path: Path):
        state = {"phase": "learning"}
        result = check_completed_has_report(state, tmp_path)
        assert result.passed

    def test_phase_completed_with_report(self, tmp_path: Path):
        state = {"phase": "completed"}
        (tmp_path / "report.md").touch()
        result = check_completed_has_report(state, tmp_path)
        assert result.passed

    def test_phase_completed_missing_report(self, tmp_path: Path):
        state = {"phase": "completed"}
        result = check_completed_has_report(state, tmp_path)
        assert not result.passed


class TestCheckLearningHasLesson:
    def test_phase_not_learning(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"phase": "init", "current_lesson": 1}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_current_lesson_zero(self, tmp_path: Path):
        state = {"phase": "learning", "current_lesson": 0}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_lesson_file_exists(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"phase": "learning", "current_lesson": 1, "last_completed_lesson": 0}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_lesson_file_missing(self, tmp_path: Path):
        state = {"phase": "learning", "current_lesson": 5, "last_completed_lesson": 4}
        result = check_learning_has_lesson(state, tmp_path)
        assert not result.passed
