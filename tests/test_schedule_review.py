"""Tests for scripts/session/schedule_review.py"""

import sys
from datetime import datetime, timezone
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.session.schedule_review import get_due_items, load_queue


class TestGetDueItems:
    def test_empty_queue(self):
        queue = {"schema_version": "1.0", "items": []}
        now = datetime.now(timezone.utc)
        assert get_due_items(queue, now) == []

    def test_status_not_pending(self):
        queue = {
            "items": [
                {
                    "lesson": 1,
                    "question_index": 0,
                    "status": "reviewed",
                    "next_review_at": "2020-01-01T00:00:00+00:00",
                }
            ]
        }
        now = datetime.now(timezone.utc)
        assert get_due_items(queue, now) == []

    def test_future_review_not_due(self):
        queue = {
            "items": [
                {
                    "lesson": 1,
                    "question_index": 0,
                    "status": "pending",
                    "next_review_at": "2099-01-01T00:00:00+00:00",
                }
            ]
        }
        now = datetime.now(timezone.utc)
        assert get_due_items(queue, now) == []

    def test_past_review_is_due(self):
        queue = {
            "items": [
                {
                    "lesson": 1,
                    "question_index": 0,
                    "status": "pending",
                    "next_review_at": "2020-01-01T00:00:00+00:00",
                }
            ]
        }
        now = datetime.now(timezone.utc)
        result = get_due_items(queue, now)
        assert len(result) == 1
        assert result[0]["lesson"] == 1

    def test_naive_datetime_normalized_to_utc(self):
        """Naive datetime (no timezone) should be treated as UTC for comparison."""
        queue = {
            "items": [
                {
                    "lesson": 2,
                    "question_index": 1,
                    "status": "pending",
                    # No timezone info - naive datetime
                    "next_review_at": "2020-01-01T00:00:00",
                }
            ]
        }
        now = datetime.now(timezone.utc)
        # Should not raise TypeError, should treat naive as UTC
        result = get_due_items(queue, now)
        assert len(result) == 1

    def test_different_timezone_normalized_to_utc(self):
        """Timezone-aware datetime should be normalized to UTC for comparison."""
        # +08:00 = 2020-01-01 00:00 local = 2019-12-31 16:00 UTC
        # If now is past that, it should be due
        queue = {
            "items": [
                {
                    "lesson": 3,
                    "question_index": 2,
                    "status": "pending",
                    "next_review_at": "2020-01-01T00:00:00+08:00",
                }
            ]
        }
        now = datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        result = get_due_items(queue, now)
        assert len(result) == 1

    def test_utc_timezone_due(self):
        queue = {
            "items": [
                {
                    "lesson": 4,
                    "question_index": 3,
                    "status": "pending",
                    "next_review_at": "2020-01-01T00:00:00+00:00",
                }
            ]
        }
        now = datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        result = get_due_items(queue, now)
        assert len(result) == 1
        assert result[0]["lesson"] == 4

    def test_utc_timezone_not_yet_due(self):
        queue = {
            "items": [
                {
                    "lesson": 5,
                    "question_index": 4,
                    "status": "pending",
                    "next_review_at": "2099-01-01T00:00:00+00:00",
                }
            ]
        }
        now = datetime.now(timezone.utc)
        result = get_due_items(queue, now)
        assert len(result) == 0


class TestLoadQueue:
    def test_no_queue_file(self, tmp_path: Path):
        result = load_queue(tmp_path)
        assert result == {"schema_version": "1.0", "items": []}

    def test_valid_queue_file(self, tmp_path: Path):
        queue_data = {
            "schema_version": "1.0",
            "items": [
                {"lesson": 1, "question_index": 0, "status": "pending"}
            ],
        }
        queue_file = tmp_path / "review_queue.json"
        queue_file.write_text(json.dumps(queue_data), encoding="utf-8")
        result = load_queue(tmp_path)
        assert result == queue_data
