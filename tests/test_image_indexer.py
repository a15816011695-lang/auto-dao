"""Tests for scripts/indexer/image_indexer.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from indexer.image_indexer import (
    _tokenize,
    _extract_tags,
    _generate_description,
    _find_nearest_heading,
    _build_heading_chain,
    build_image_index,
)
from indexer.md_parser import Heading


class TestTokenizeImage:
    """Image indexer's _tokenize shares logic with corpus_indexer but is defined separately."""

    def test_basic_tokenization(self):
        result = _tokenize("这是测试文本")
        assert len(result) > 0
        assert "测试" in result

    def test_english_tokenization(self):
        result_lower = [t.lower() for t in _tokenize("Serial Peripheral Interface SPI")]
        assert "serial" in result_lower
        assert "spi" in result_lower

    def test_stopwords_filtered(self):
        result = _tokenize("这是的和在了")
        assert "这" not in result
        assert "是" not in result

    def test_short_tokens_filtered(self):
        result = _tokenize("I A 你 好")
        for token in result:
            assert len(token) >= 2


class TestExtractTags:
    def test_max_15_tags(self):
        """Should return at most 15 tags."""
        text = " ".join([f"word{i}" for i in range(50)])
        result = _extract_tags(text)
        assert len(result) <= 15

    def test_no_duplicates(self):
        text = "串行通信 SPI 串行通信 SPI"
        result = _extract_tags(text)
        assert len(result) == len(set(result))

    def test_empty_text(self):
        assert _extract_tags("") == []
        # All stopwords
        assert _extract_tags("的是在了和") == []

    def test_deduplication_preserves_order(self):
        """First occurrence order should be preserved."""
        text = "SPI 协议 SPI 通信 协议"
        result = _extract_tags(text)
        assert result.count("SPI") == 1
        assert result.index("SPI") < result.index("通信")

    def test_chinese_technical_terms(self):
        text = "STM32单片机嵌入式系统开发板GPIO引脚"
        result = _extract_tags(text)
        assert len(result) > 0


class TestFindNearestHeading:
    def test_returns_last_h1_or_h2(self):
        """Should return the nearest heading before or at current position."""
        headings = [
            Heading(1, "Top Level", "# Top Level"),
            Heading(2, "Section", "## Section"),
            Heading(3, "Subsection", "### Subsection"),
        ]
        result = _find_nearest_heading(10, headings)
        # Without line numbers in Heading, returns last H1/H2
        assert result is not None
        assert result.level in (1, 2)

    def test_returns_none_when_no_h1_h2(self):
        headings = [
            Heading(3, "Subsection", "### Subsection"),
            Heading(4, "Sub-subsection", "#### Sub-subsection"),
        ]
        result = _find_nearest_heading(10, headings)
        assert result is None

    def test_empty_headings(self):
        result = _find_nearest_heading(10, [])
        assert result is None


class TestBuildHeadingChain:
    def test_limits_to_5_levels(self):
        headings = [
            Heading(1, "H1", "# H1"),
            Heading(2, "H2", "## H2"),
            Heading(3, "H3", "### H3"),
            Heading(4, "H4", "#### H4"),
            Heading(5, "H5", "##### H5"),
            Heading(6, "H6", "###### H6"),
        ]
        result = _build_heading_chain(10, headings)
        assert len(result) <= 5

    def test_only_h1_h2(self):
        headings = [
            Heading(1, "H1", "# H1"),
            Heading(2, "H2", "## H2"),
            Heading(3, "H3", "### H3"),
        ]
        result = _build_heading_chain(10, headings)
        assert len(result) == 2
        assert result[0] == "H1"
        assert result[1] == "H2"

    def test_empty_headings(self):
        result = _build_heading_chain(10, [])
        assert result == []


class TestGenerateDescription:
    def test_with_heading_and_sentence(self):
        """Heading + first sentence should be combined."""
        headings = [Heading(1, "SPI 协议", "# SPI 协议")]
        from indexer.md_parser import ImageRef
        ref = ImageRef(
            hash="abc",
            line_no=5,
            context_before="SPI 是串行外设接口。这是一种同步通信协议。",
            context_after="下一节内容。",
        )
        result = _generate_description(ref, headings)
        assert "SPI 协议" in result
        assert len(result) <= 50

    def test_heading_only_no_sentence(self):
        """If no complete sentence in context, use heading only."""
        headings = [Heading(2, "时钟信号", "## 时钟信号")]
        from indexer.md_parser import ImageRef
        ref = ImageRef(
            hash="xyz",
            line_no=10,
            context_before="",
            context_after="",
        )
        result = _generate_description(ref, headings)
        assert result == "时钟信号"

    def test_sentence_truncated_at_50(self):
        """Description should be truncated at 50 characters."""
        headings = []
        from indexer.md_parser import ImageRef
        ref = ImageRef(
            hash="long",
            line_no=1,
            context_before="A" * 100,
            context_after="",
        )
        result = _generate_description(ref, headings)
        assert len(result) <= 50

    def test_no_context_returns_default(self):
        """If no heading and no sentence, should return '图片'."""
        from indexer.md_parser import ImageRef
        ref = ImageRef(hash="x", line_no=1, context_before="", context_after="")
        result = _generate_description(ref, [])
        assert result == "图片"


class TestBuildImageIndex:
    def test_meta_structure(self, tmp_path: Path):
        """Verify _meta structure of output."""
        folder = tmp_path / "test_mat"
        folder.mkdir()
        (folder / "full.md").write_text("# Test\n\nText\n", encoding="utf-8")
        images = folder / "images"
        images.mkdir()

        result = build_image_index(folder)
        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "total_images" in result["_meta"]
        assert "generated" in result["_meta"]
        assert "images" in result

    def test_no_images(self, tmp_path: Path):
        """full.md without images should return empty images list."""
        folder = tmp_path / "no_img"
        folder.mkdir()
        (folder / "full.md").write_text("# Title\n\nPlain text without images.\n", encoding="utf-8")
        (folder / "images").mkdir()

        result = build_image_index(folder)
        assert result["_meta"]["total_images"] == 0
        assert result["images"] == []

    def test_image_file_exists(self, tmp_path: Path):
        """Image with existing file should include path and size."""
        folder = tmp_path / "with_img"
        folder.mkdir()
        (folder / "full.md").write_text(
            "Text\n![desc](images/abc123.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()
        # Create a small image file
        img_path = images / "abc123.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"x" * 100)

        result = build_image_index(folder)
        assert len(result["images"]) == 1
        img = result["images"][0]
        assert img["filename"] == "abc123.jpg"
        assert img["size_bytes"] > 0

    def test_image_file_missing(self, tmp_path: Path):
        """Image referenced but file not on disk should have empty path and size 0."""
        folder = tmp_path / "missing_img"
        folder.mkdir()
        (folder / "full.md").write_text(
            "Text\n![desc](images/nonexistent.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()  # No actual image file

        result = build_image_index(folder)
        img = result["images"][0]
        assert img["path"] == ""
        assert img["size_bytes"] == 0

    def test_multiple_images(self, tmp_path: Path):
        """Multiple images should each get their own entry."""
        folder = tmp_path / "multi_img"
        folder.mkdir()
        (folder / "full.md").write_text(
            "Text\n![a](images/img1.jpg)\nText\n![b](images/img2.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()
        (images / "img1.jpg").write_bytes(b"\xff\xd8\xff")
        (images / "img2.jpg").write_bytes(b"\xff\xd8\xff")

        result = build_image_index(folder)
        assert len(result["images"]) == 2
        assert result["_meta"]["total_images"] == 2

    def test_heading_chain_extracted(self, tmp_path: Path):
        """Each image should have its heading chain extracted."""
        folder = tmp_path / "heading_test"
        folder.mkdir()
        (folder / "full.md").write_text(
            "# 顶层章节\n\n## 子章节\n\n![desc](images/abc003.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()
        (images / "abc003.jpg").write_bytes(b"\xff\xd8\xff")

        result = build_image_index(folder)
        img = result["images"][0]
        assert "顶层章节" in img["headings"]
        assert "子章节" in img["headings"]

    def test_description_generated(self, tmp_path: Path):
        """Each image should have a generated description."""
        folder = tmp_path / "desc_test"
        folder.mkdir()
        (folder / "full.md").write_text(
            "# STM32开发板\n\n![开发板](images/abc001.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()
        (images / "abc001.jpg").write_bytes(b"\xff\xd8\xff")

        result = build_image_index(folder)
        img = result["images"][0]
        assert img["description"] != ""
        assert len(img["description"]) <= 50

    def test_tags_extracted(self, tmp_path: Path):
        """Each image should have extracted tags."""
        folder = tmp_path / "tags_test"
        folder.mkdir()
        (folder / "full.md").write_text(
            "STM32单片机GPIO引脚配置\n![引脚图](images/abc002.jpg)\n",
            encoding="utf-8",
        )
        images = folder / "images"
        images.mkdir()
        (images / "abc002.jpg").write_bytes(b"\xff\xd8\xff")

        result = build_image_index(folder)
        img = result["images"][0]
        assert len(img["tags"]) > 0
        assert len(img["tags"]) <= 15


# ---------------------------------------------------------------------------
# Helper: pytest import
# ---------------------------------------------------------------------------
import pytest  # noqa: F401, E402
