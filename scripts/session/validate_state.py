#!/usr/bin/env python3
"""
validate_state.py — auto-dao session state validator

Checks the consistency between session_state.json and the actual
directory structure of a learning session. Designed to be run by
humans or CI, not by the AI model itself.

Usage:
    python scripts/session/validate_state.py <session_dir>

Example:
    python scripts/session/validate_state.py learning-history/stm32-hal_2026-04-13-09-45

Exit codes:
    0  — all checks passed
    1  — one or more checks failed
    2  — fatal error (missing files, bad JSON, etc.)
"""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "learning-engine" / "templates" / "session-state.schema.json"
with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
    _SCHEMA = json.load(f)

SCHEMA_VERSION = _SCHEMA["properties"]["schema_version"]["const"]
VALID_PHASES = set(_SCHEMA["properties"]["phase"]["enum"])
VALID_CF_MODES = set(_SCHEMA["properties"]["counterfactual_mode"]["enum"])
VALID_WAIT_REASONS = set(_SCHEMA["properties"]["wait_reason"]["enum"])
REQUIRED_FIELDS = set(_SCHEMA["required"])


def _lesson_indices(lessons_dir: Path) -> list[int]:
    """Return sorted list of lesson indices found in lessons/ directory."""
    indices = []
    for f in lessons_dir.iterdir():
        m = re.match(r"lesson_(\d+)\.md$", f.name)
        if m:
            indices.append(int(m.group(1)))
    return sorted(indices)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail

    def __str__(self):
        if sys.platform == "win32":
            mark = "[PASS]" if self.passed else "[FAIL]"
        else:
            mark = "✅" if self.passed else "❌"
        msg = f"{mark} [{self.name}]"
        if self.detail:
            msg += f"  {self.detail}"
        return msg


def check_schema_version(state: dict) -> CheckResult:
    v = state.get("schema_version")
    ok = v == SCHEMA_VERSION
    return CheckResult(
        "schema_version",
        ok,
        f"expected '{SCHEMA_VERSION}', got '{v}'" if not ok else "",
    )


def check_required_fields(state: dict) -> CheckResult:
    missing = [f for f in REQUIRED_FIELDS if f not in state]
    ok = len(missing) == 0
    return CheckResult(
        "required_fields",
        ok,
        f"missing: {missing}" if not ok else "",
    )


def check_phase(state: dict) -> CheckResult:
    phase = state.get("phase")
    ok = phase in VALID_PHASES
    return CheckResult(
        "phase_valid",
        ok,
        f"'{phase}' not in {VALID_PHASES}" if not ok else "",
    )


def check_counterfactual_mode(state: dict) -> CheckResult:
    mode = state.get("counterfactual_mode")
    ok = mode in VALID_CF_MODES
    return CheckResult(
        "counterfactual_mode",
        ok,
        f"'{mode}' not in {VALID_CF_MODES}" if not ok else "",
    )


def check_wait_reason(state: dict) -> CheckResult:
    reason = state.get("wait_reason")
    ok = reason in VALID_WAIT_REASONS
    return CheckResult(
        "wait_reason",
        ok,
        f"'{reason}' not in {VALID_WAIT_REASONS}" if not ok else "",
    )


def check_lesson_count(state: dict, lessons_dir: Path) -> CheckResult:
    """current_lesson should match the highest lesson file index."""
    if not lessons_dir.exists():
        if state.get("current_lesson", 0) == 0:
            return CheckResult("lesson_count", True, "no lessons dir, current_lesson=0")
        return CheckResult("lesson_count", False, "lessons/ dir missing but current_lesson > 0")

    indices = _lesson_indices(lessons_dir)
    max_index = max(indices) if indices else 0
    current = state.get("current_lesson", 0)
    # current_lesson should be max_index or max_index+1 (next to generate)
    ok = current in (max_index, max_index + 1)
    return CheckResult(
        "lesson_count",
        ok,
        f"current_lesson={current}, max file index={max_index}" if not ok else "",
    )


def check_lesson_continuity(lessons_dir: Path) -> CheckResult:
    """Lesson files should be numbered sequentially starting from 1, with gaps allowed for remedial/branch lessons."""
    if not lessons_dir.exists():
        return CheckResult("lesson_continuity", True, "no lessons dir")
    indices = _lesson_indices(lessons_dir)
    if not indices:
        return CheckResult("lesson_continuity", True, "no lesson files")
    # Allow gaps due to remedial/branch lessons (lesson_N_remedial.md, lesson_N_branch.md)
    # Check: sorted, unique, starts at 1
    ok = indices == sorted(set(indices)) and indices[0] == 1
    return CheckResult(
        "lesson_continuity",
        ok,
        f"indices must start at 1 and be unique, got {indices}" if not ok else "",
    )


def check_completed_has_report(state: dict, session_dir: Path) -> CheckResult:
    """If phase is 'completed', report.md should exist."""
    phase = state.get("phase")
    if phase != "completed":
        return CheckResult("completed_report", True, "phase != completed, skipped")
    report = session_dir / "report.md"
    ok = report.exists()
    return CheckResult(
        "completed_report",
        ok,
        "phase=completed but report.md missing" if not ok else "",
    )


def check_mastery_rate(state: dict) -> CheckResult:
    """mastery_rate should equal passed/(passed+failed) if there are attempts."""
    passed = state.get("mastery_passed", 0)
    failed = state.get("mastery_failed", 0)
    rate = state.get("mastery_rate", 0.0)
    total = passed + failed
    if total == 0:
        ok = rate == 0.0
        return CheckResult("mastery_rate", ok, f"no attempts but rate={rate}" if not ok else "")
    expected = round(passed / total, 4)
    actual = round(rate, 4)
    ok = abs(expected - actual) < 0.01
    return CheckResult(
        "mastery_rate",
        ok,
        f"expected ~{expected}, got {actual}" if not ok else "",
    )


def check_learning_has_lesson(state: dict, lessons_dir: Path) -> CheckResult:
    """If phase='learning' and current_lesson > 0, that lesson file should exist."""
    phase = state.get("phase")
    current = state.get("current_lesson", 0)
    if phase != "learning" or current == 0:
        return CheckResult("learning_has_lesson", True, "skipped (phase or lesson 0)")
    # The file for the current lesson being worked on (or last generated)
    last = state.get("last_completed_lesson", 0)
    check_index = max(current, last)
    if check_index == 0:
        return CheckResult("learning_has_lesson", True, "no lessons yet")
    target = lessons_dir / f"lesson_{check_index}.md"
    ok = target.exists()
    return CheckResult(
        "learning_has_lesson",
        ok,
        f"lesson_{check_index}.md missing" if not ok else "",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(session_dir: Path) -> list[CheckResult]:
    state_file = session_dir / "session_state.json"
    lessons_dir = session_dir / "lessons"

    if not state_file.exists():
        return [CheckResult("file_exists", False, f"{state_file} not found")]

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        return [CheckResult("json_parse", False, str(e))]

    results = [
        check_schema_version(state),
        check_required_fields(state),
        check_phase(state),
        check_counterfactual_mode(state),
        check_wait_reason(state),
        check_lesson_count(state, lessons_dir),
        check_lesson_continuity(lessons_dir),
        check_completed_has_report(state, session_dir),
        check_mastery_rate(state),
        check_learning_has_lesson(state, lessons_dir),
    ]
    return results


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <session_dir>", file=sys.stderr)
        sys.exit(2)

    session_dir = Path(sys.argv[1])
    if not session_dir.is_dir():
        print(f"Error: '{session_dir}' is not a directory", file=sys.stderr)
        sys.exit(2)

    results = validate(session_dir)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for r in results:
        print(r)
    print(f"\n{'=' * 40}")
    print(f"Result: {passed}/{total} checks passed")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
