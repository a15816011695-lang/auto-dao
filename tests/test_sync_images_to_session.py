"""Tests for scripts/indexer/sync_images_to_session.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# conftest.py already puts scripts/ on sys.path; this is a safety repeat.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from indexer.sync_images_to_session import (  # noqa: E402
    copy_images,
    find_source_index,
    rewrite_paths_for_session,
    sync,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_material_and_index(
    tmp_path: Path,
    material_name: str = "04-STM32F103HAL库开发_20260413_094457",
    index_label: str = "04-STM32F103HAL库开发",
    image_hashes: tuple[str, ...] = ("abc123", "def456"),
) -> tuple[Path, Path]:
    """Build a fake tmp/converted/{material}/ + tmp/converted/index/{label}/.

    Returns (processed_path, source_index_path).
    """
    converted = tmp_path / "tmp" / "converted"
    processed = converted / material_name
    images_dir = processed / "images"
    images_dir.mkdir(parents=True)

    # Create fake image files.
    for h in image_hashes:
        (images_dir / f"{h}.jpg").write_bytes(b"\xff\xd8\xff\xe0 dummy " + h.encode())

    # Create the full.md file (not strictly required by sync, but realistic).
    (processed / "full.md").write_text(
        "# 测试资料\n\n![图示](images/abc123.jpg)\n\n正文。\n",
        encoding="utf-8",
    )

    # Build a source index that mimics image_indexer.py output shape.
    index_dir = converted / "index" / index_label
    index_dir.mkdir(parents=True)
    source_index = {
        "_meta": {
            "source": index_label,
            "total_images": len(image_hashes),
            "generated": "2026-04-15",
        },
        "images": [
            {
                "filename": f"{h}.jpg",
                "path": f"{material_name}/images/{h}.jpg",
                "description": f"图片 {h} 描述",
                "tags": ["测试", "示例"],
                "headings": ["第一章"],
                "page_approx": 1,
                "size_bytes": 20,
            }
            for h in image_hashes
        ],
    }
    index_path = index_dir / "image_index.json"
    index_path.write_text(json.dumps(source_index, ensure_ascii=False), encoding="utf-8")

    return processed, index_path


def _make_session(tmp_path: Path) -> Path:
    """Create a minimal session directory (mirrors learning-history/{topic}_{ts}/)."""
    session = tmp_path / "learning-history" / "test-topic_2026-04-15-10-00"
    (session / "lessons").mkdir(parents=True)
    return session


# ---------------------------------------------------------------------------
# Unit tests: pure-function helpers
# ---------------------------------------------------------------------------

class TestFindSourceIndex:
    def test_returns_path_when_index_exists(self, tmp_path: Path):
        processed, index_path = _make_material_and_index(tmp_path)
        assert find_source_index(processed) == index_path

    def test_returns_none_when_index_missing(self, tmp_path: Path):
        converted = tmp_path / "tmp" / "converted"
        processed = converted / "material_no_index_20260101_000000"
        processed.mkdir(parents=True)
        assert find_source_index(processed) is None


class TestRewritePathsForSession:
    def test_strips_material_folder_prefix(self):
        index = {
            "_meta": {"source": "X", "total_images": 1},
            "images": [
                {"path": "mymaterial_20260101_000000/images/abc.jpg", "filename": "abc.jpg"},
            ],
        }
        out = rewrite_paths_for_session(index, "mymaterial_20260101_000000")
        assert out["images"][0]["path"] == "images/abc.jpg"

    def test_leaves_unrelated_path_untouched(self):
        index = {
            "images": [
                {"path": "external/x.jpg"},
            ],
        }
        out = rewrite_paths_for_session(index, "unrelated")
        assert out["images"][0]["path"] == "external/x.jpg"

    def test_adds_session_local_meta(self):
        index = {"_meta": {"source": "X"}, "images": []}
        out = rewrite_paths_for_session(index, "X_20260101_000000")
        assert out["_meta"]["session_local"] is True
        assert out["_meta"]["source_material_folder"] == "X_20260101_000000"

    def test_preserves_other_fields(self):
        """Rewriting must not drop description/tags/etc."""
        index = {
            "images": [
                {
                    "filename": "abc.jpg",
                    "path": "mat_20260101_000000/images/abc.jpg",
                    "description": "Signal timing diagram",
                    "tags": ["I2C", "timing"],
                    "headings": ["第11章"],
                    "page_approx": 42,
                    "size_bytes": 1234,
                }
            ],
        }
        out = rewrite_paths_for_session(index, "mat_20260101_000000")
        img = out["images"][0]
        assert img["description"] == "Signal timing diagram"
        assert img["tags"] == ["I2C", "timing"]
        assert img["headings"] == ["第11章"]
        assert img["page_approx"] == 42
        assert img["size_bytes"] == 1234


class TestCopyImages:
    def test_copies_all_files(self, tmp_path: Path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.jpg").write_bytes(b"aaa")
        (src / "b.jpg").write_bytes(b"bbbb")
        dst = tmp_path / "dst"

        copied, skipped = copy_images(src, dst)
        assert copied == 2
        assert skipped == 0
        assert (dst / "a.jpg").read_bytes() == b"aaa"
        assert (dst / "b.jpg").read_bytes() == b"bbbb"

    def test_skips_identical_existing_files(self, tmp_path: Path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.jpg").write_bytes(b"aaa")
        dst = tmp_path / "dst"
        dst.mkdir()
        (dst / "a.jpg").write_bytes(b"aaa")  # same size

        copied, skipped = copy_images(src, dst)
        assert copied == 0
        assert skipped == 1

    def test_recopies_different_sized_files(self, tmp_path: Path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.jpg").write_bytes(b"aaaXXX")  # 6 bytes
        dst = tmp_path / "dst"
        dst.mkdir()
        (dst / "a.jpg").write_bytes(b"aaa")  # 3 bytes, stale

        copied, skipped = copy_images(src, dst)
        assert copied == 1
        assert skipped == 0
        assert (dst / "a.jpg").read_bytes() == b"aaaXXX"

    def test_missing_source_returns_zero(self, tmp_path: Path):
        copied, skipped = copy_images(tmp_path / "nonexistent", tmp_path / "dst")
        assert (copied, skipped) == (0, 0)


# ---------------------------------------------------------------------------
# Integration test: full sync
# ---------------------------------------------------------------------------

class TestSyncIntegration:
    def test_full_sync_creates_session_local_index_and_copies_images(self, tmp_path: Path):
        processed, _ = _make_material_and_index(tmp_path)
        session = _make_session(tmp_path)

        result = sync(processed, session, auto_build=False)

        # Session-local index exists
        session_index_path = session / "image_index.json"
        assert session_index_path.exists()

        # Paths were rewritten
        data = json.loads(session_index_path.read_text(encoding="utf-8"))
        for img in data["images"]:
            assert img["path"].startswith("images/"), (
                f"path not rewritten: {img['path']}"
            )
            # Verify the actual file exists at the rewritten path
            physical = session / img["path"]
            assert physical.is_file(), f"missing image file: {physical}"

        # Session-local meta was added
        assert data["_meta"]["session_local"] is True
        assert "source_material_folder" in data["_meta"]

        # Stats match
        assert result["copied"] == 2
        assert result["total_in_index"] == 2

    def test_sync_is_idempotent(self, tmp_path: Path):
        """Running sync twice should not re-copy unchanged files."""
        processed, _ = _make_material_and_index(tmp_path)
        session = _make_session(tmp_path)

        first = sync(processed, session, auto_build=False)
        second = sync(processed, session, auto_build=False)

        assert first["copied"] == 2
        assert second["copied"] == 0
        assert second["skipped"] == 2

    def test_sync_raises_when_index_missing_and_no_auto_build(self, tmp_path: Path):
        """Without auto-build, a missing index must surface as FileNotFoundError."""
        converted = tmp_path / "tmp" / "converted"
        processed = converted / "mat_no_index_20260101_000000"
        (processed / "images").mkdir(parents=True)
        session = _make_session(tmp_path)

        with pytest.raises(FileNotFoundError, match="image_index.json not found"):
            sync(processed, session, auto_build=False)

    def test_sync_rejects_missing_processed_path(self, tmp_path: Path):
        session = _make_session(tmp_path)
        with pytest.raises(FileNotFoundError, match="processed_path not found"):
            sync(tmp_path / "nope", session, auto_build=False)

    def test_sync_rejects_missing_session_dir(self, tmp_path: Path):
        processed, _ = _make_material_and_index(tmp_path)
        with pytest.raises(FileNotFoundError, match="session_dir not found"):
            sync(processed, tmp_path / "nope", auto_build=False)
