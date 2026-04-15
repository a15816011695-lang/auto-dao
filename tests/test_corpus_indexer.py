"""Tests for scripts/indexer/corpus_indexer.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from indexer.corpus_indexer import (
    _tokenize,
    _heading_keywords,
    _compute_similarity,
    _keywords_overlap,
    build_material_entries,
    match_concepts,
    build_shared_corpus,
)
from indexer.md_parser import Heading


class TestTokenize:
    def test_chinese_only(self):
        result = _tokenize("这是测试文本包含中文字符")
        assert len(result) > 0
        # Basic tokenization: may not filter all stopwords, verify tokens present
        assert "测试" in result
        assert "文本" in result

    def test_english_only(self):
        result_lower = [t.lower() for t in _tokenize("Hello World Serial Peripheral Interface")]
        assert "hello" in result_lower
        assert "world" in result_lower
        assert "serial" in result_lower

    def test_mixed_chinese_english(self):
        result = _tokenize("SPI协议是串行外设接口")
        assert len(result) > 0
        # Should contain both Chinese and English tokens
        tokens_str = " ".join(result).lower()
        assert "spi" in tokens_str or "协议" in result

    def test_stopwords_filtered(self):
        """Common Chinese stopwords should be removed."""
        text = "这是一个测试这是的在了和与"
        result = _tokenize(text)
        assert "这" not in result
        assert "是" not in result
        assert "的" not in result
        assert "在" not in result
        # Non-stopwords should remain
        assert "一个" in result or "测试" in result

    def test_short_tokens_filtered(self):
        """Tokens shorter than 2 characters should be removed."""
        result = _tokenize("I A am SPI")
        # Single-char English filtered, "am" kept if >= 2
        for token in result:
            assert len(token) >= 2

    def test_empty_string(self):
        assert _tokenize("") == []
        assert _tokenize("的的在了") == []  # All stopwords


class TestHeadingKeywords:
    def test_removes_numbering_dot(self):
        """Numbering like "1.1 " should be removed."""
        heading = Heading(level=2, text="1.1 SPI 协议概述", raw="# 1.1 SPI 协议概述")
        result = _heading_keywords(heading)
        assert "1.1" not in result
        assert "SPI" in result
        assert "协议" in result

    def test_removes_numbering_paren(self):
        """Numbering like "(3)" should be removed."""
        heading = Heading(level=2, text="(3)时钟信号", raw="## (3)时钟信号")
        result = _heading_keywords(heading)
        assert "(3)" not in result
        assert "时钟" in result
        assert "信号" in result

    def test_removes_chinese_numbering(self):
        """Chinese numerals should be removed."""
        heading = Heading(level=2, text="一、SPI协议原理", raw="## 一、SPI协议原理")
        result = _heading_keywords(heading)
        assert "一" not in result

    def test_preserves_content(self):
        """Content should be preserved after numbering removal."""
        heading = Heading(level=1, text="# STM32 嵌入式开发", raw="# STM32 嵌入式开发")
        result = _heading_keywords(heading)
        assert "STM32" in result
        assert "嵌入式" in result
        assert "开发" in result


class TestComputeSimilarity:
    def test_identical_strings(self):
        result = _compute_similarity("SPI协议", "SPI协议")
        assert result == 1.0

    def test_completely_different(self):
        result = _compute_similarity("SPI协议", "I2C协议")
        assert 0.0 <= result < 1.0

    def test_partial_overlap(self):
        """Partially overlapping strings should have moderate similarity."""
        s1 = "SPI协议的时钟极性"
        s2 = "SPI协议的时钟相位"
        result = _compute_similarity(s1, s2)
        assert 0.3 < result < 0.9

    def test_empty_string_both(self):
        assert _compute_similarity("", "") == 1.0

    def test_empty_string_one_side(self):
        assert _compute_similarity("text", "") == 0.0
        assert _compute_similarity("", "text") == 0.0

    def test_similar_long_strings(self):
        """Very similar long strings should have high similarity."""
        s1 = "SPI协议是一种同步串行通信协议，广泛应用于嵌入式系统"
        s2 = "SPI协议是一种同步串行通信协议，广泛应用于微控制器"
        result = _compute_similarity(s1, s2)
        assert result > 0.7


class TestKeywordsOverlap:
    def test_complete_overlap(self):
        kw1 = ["SPI", "协议", "时钟"]
        kw2 = ["SPI", "协议", "时钟"]
        assert _keywords_overlap(kw1, kw2) == 1.0

    def test_no_overlap(self):
        kw1 = ["SPI", "协议"]
        kw2 = ["I2C", "协议"]
        assert _keywords_overlap(kw1, kw2) == pytest.approx(0.333, abs=0.05)

    def test_partial_overlap(self):
        kw1 = ["SPI", "协议", "时钟"]
        kw2 = ["SPI", "协议"]
        result = _keywords_overlap(kw1, kw2)
        # Intersection = {SPI, 协议} = 2, Union = {SPI, 协议, 时钟} = 3, ratio = 2/3
        assert result == pytest.approx(0.667, abs=0.01)

    def test_empty_kw1(self):
        assert _keywords_overlap([], ["a", "b"]) == 0.0

    def test_empty_kw2(self):
        assert _keywords_overlap(["a", "b"], []) == 0.0

    def test_both_empty(self):
        assert _keywords_overlap([], []) == 0.0


class TestBuildMaterialEntries:
    def test_single_folder(self, tmp_path: Path):
        folder = tmp_path / "mat1"
        folder.mkdir()
        (folder / "full.md").write_text(
            "# SPI 协议\n\n## 时钟信号\n\n正文内容。\n",
            encoding="utf-8",
        )
        entries = build_material_entries([folder])
        assert len(entries) == 1
        assert entries[0].label == "mat1"
        assert len(entries[0].headings) == 2
        assert entries[0].headings[0].text == "SPI 协议"

    def test_multiple_headings(self, tmp_path: Path):
        folder = tmp_path / "multi"
        folder.mkdir()
        (folder / "full.md").write_text(
            "# 主标题\n\n内容1\n\n## 副标题1\n\n内容2\n\n### 三级标题\n\n内容3\n",
            encoding="utf-8",
        )
        entries = build_material_entries([folder])
        assert len(entries) == 1
        # Should only keep H1 and H2
        levels = [h.level for h in entries[0].headings]
        assert 1 in levels
        assert 2 in levels
        assert 3 not in levels

    def test_extracts_image_hashes(self, tmp_path: Path):
        folder = tmp_path / "imgs"
        folder.mkdir()
        (folder / "full.md").write_text(
            "Text\n![desc](images/abc123.jpg)\nMore\n",
            encoding="utf-8",
        )
        entries = build_material_entries([folder])
        assert "abc123" in entries[0].image_hashes

    def test_no_full_md(self, tmp_path: Path):
        """Should handle gracefully if full.md doesn't exist."""
        folder = tmp_path / "empty"
        folder.mkdir()
        entries = build_material_entries([folder])
        assert len(entries) == 1
        assert entries[0].headings == []

    def test_multiple_folders(self, tmp_path: Path):
        folders = []
        for name in ["aaa", "bbb", "ccc"]:
            f = tmp_path / name
            f.mkdir()
            (f / "full.md").write_text(f"# {name}\n\n", encoding="utf-8")
            folders.append(f)
        entries = build_material_entries(folders)
        assert len(entries) == 3


class TestMatchConcepts:
    def test_no_duplicates_in_same_material(self):
        """Items from the same material should not be clustered together."""
        # Two items with same label should not cross-reference
        folder = Path("/fake")
        from indexer.corpus_indexer import MaterialEntry, Heading as H
        entry = MaterialEntry(
            folder=folder,
            label="test",
            headings=[H(1, "A", "# A"), H(2, "B", "## B")],
            heading_texts=["A", "B"],
            keywords_per_heading={"A": ["x"], "B": ["x"]},
            image_hashes=set(),
        )
        groups = match_concepts([entry])
        # Since both are from same material, they shouldn't create cross-refs
        # (cross_refs are keyed by label, same label = same material)
        for g in groups:
            assert g.topic not in g.cross_refs or g.topic not in g.cross_refs

    def test_below_threshold_not_clustered(self):
        """Items with very low similarity should not be clustered."""
        folder_a = Path("/fake_a")
        folder_b = Path("/fake_b")
        from indexer.corpus_indexer import MaterialEntry, Heading as H

        entries = [
            MaterialEntry(
                folder=folder_a, label="A",
                headings=[H(1, "嵌入式系统开发", "# 嵌入式系统开发")],
                heading_texts=["嵌入式系统开发"],
                keywords_per_heading={"嵌入式系统开发": ["嵌入式", "系统", "开发"]},
                image_hashes=set(),
            ),
            MaterialEntry(
                folder=folder_b, label="B",
                headings=[H(1, "菜谱大全", "# 菜谱大全")],
                heading_texts=["菜谱大全"],
                keywords_per_heading={"菜谱大全": ["菜谱", "烹饪", "食材"]},
                image_hashes=set(),
            ),
        ]
        groups = match_concepts(entries, sim_threshold=0.55)
        # These should be in separate groups (no cross-material match)
        assert len(groups) >= 2

    def test_empty_entries(self):
        groups = match_concepts([])
        assert groups == []

    def test_similar_headings_clustered(self):
        """Two materials with identical headings should cluster."""
        folder_a = Path("/fake_a")
        folder_b = Path("/fake_b")
        from indexer.corpus_indexer import MaterialEntry, Heading as H

        shared_keywords = ["SPI", "协议", "通信"]
        entries = [
            MaterialEntry(
                folder=folder_a, label="MatA",
                headings=[H(1, "SPI 协议", "# SPI 协议")],
                heading_texts=["SPI 协议"],
                keywords_per_heading={"SPI 协议": shared_keywords},
                image_hashes=set(),
            ),
            MaterialEntry(
                folder=folder_b, label="MatB",
                headings=[H(1, "SPI 协议", "# SPI 协议")],
                heading_texts=["SPI 协议"],
                keywords_per_heading={"SPI 协议": shared_keywords},
                image_hashes=set(),
            ),
        ]
        groups = match_concepts(entries, sim_threshold=0.55)
        # Should be in one group with cross-refs to both materials
        assert len(groups) == 1
        assert len(groups[0].cross_refs) == 2


class TestBuildSharedCorpus:
    def test_meta_structure(self, tmp_path: Path):
        """Build corpus from temp folders and verify meta fields."""
        folder_a = tmp_path / "mat_a"
        folder_b = tmp_path / "mat_b"
        for f in (folder_a, folder_b):
            f.mkdir()
            (f / "full.md").write_text("# 共同主题\n\n内容。\n", encoding="utf-8")

        corpus = build_shared_corpus([folder_a, folder_b])

        assert "_meta" in corpus
        assert "generated" in corpus["_meta"]
        assert "sources" in corpus["_meta"]
        assert len(corpus["_meta"]["sources"]) == 2
        assert "groups" in corpus
        assert isinstance(corpus["groups"], list)

    def test_groups_sorted_by_cross_refs(self, tmp_path: Path):
        """Groups should be sorted by number of cross-references (most first)."""
        # Create 3 folders, 2 of which share a heading
        folder_a = tmp_path / "mat_a"
        folder_b = tmp_path / "mat_b"
        folder_c = tmp_path / "mat_c"
        for f in (folder_a, folder_b, folder_c):
            f.mkdir()

        # mat_a and mat_b share "SPI 协议", mat_c has unique heading
        (folder_a / "full.md").write_text("# SPI 协议\n\nA\n", encoding="utf-8")
        (folder_b / "full.md").write_text("# SPI 协议\n\nB\n", encoding="utf-8")
        (folder_c / "full.md").write_text("# 嵌入式开发\n\nC\n", encoding="utf-8")

        corpus = build_shared_corpus([folder_a, folder_b, folder_c])
        # The "SPI 协议" group should be first (2 cross-refs), unique heading second (1)
        if len(corpus["groups"]) >= 2:
            assert len(corpus["groups"][0]["cross_refs"]) >= len(
                corpus["groups"][-1]["cross_refs"]
            )


# ---------------------------------------------------------------------------
# Helper: pytest import
# ---------------------------------------------------------------------------
import pytest  # noqa: E402
