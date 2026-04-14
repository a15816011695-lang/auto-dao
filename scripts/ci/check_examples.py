#!/usr/bin/env python3
"""
check_examples.py — Validate example learning-history directory structure.

Each example session under examples/learning-history/ must contain:
  - summary.md
  - roadmap_status.md
  - lessons/           (directory with at least one lesson_N.md)

Exit codes:
    0  — all examples valid
    1  — one or more examples invalid
"""

import re
import sys
from pathlib import Path

EXAMPLES_ROOT = Path("examples/learning-history")

REQUIRED_FILES = ["summary.md", "roadmap_status.md"]
SKIP = {"README.md"}


def check_session(session_dir: Path) -> list[str]:
    """Return list of error messages for a single session directory."""
    errors = []

    for fname in REQUIRED_FILES:
        if not (session_dir / fname).exists():
            errors.append(f"missing {fname}")

    lessons_dir = session_dir / "lessons"
    if not lessons_dir.is_dir():
        errors.append("missing lessons/ directory")
    else:
        lesson_files = [
            f for f in lessons_dir.iterdir()
            if re.match(r"lesson_\d+\.md$", f.name)
        ]
        if not lesson_files:
            errors.append("lessons/ contains no lesson_N.md files")

    return errors


def main():
    if not EXAMPLES_ROOT.is_dir():
        print(f"ERROR: {EXAMPLES_ROOT} not found")
        sys.exit(1)

    sessions = [
        d for d in EXAMPLES_ROOT.iterdir()
        if d.is_dir() and d.name not in SKIP
    ]

    if not sessions:
        print(f"WARNING: no example sessions found in {EXAMPLES_ROOT}")
        sys.exit(0)

    total_errors = 0

    for session in sorted(sessions):
        errors = check_session(session)
        if errors:
            total_errors += len(errors)
            for err in errors:
                print(f"❌ {session.name}: {err}")
        else:
            print(f"✅ {session.name}")

    print(f"\n{'=' * 40}")
    print(f"Checked {len(sessions)} examples, {total_errors} errors")

    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
