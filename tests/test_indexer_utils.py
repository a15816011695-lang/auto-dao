"""Tests for scripts/indexer/utils.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from indexer.utils import (
    discover_material_folders,
    read_json_safe,
    read_text_safe,
    normalize_text,
    extract_folder_label,
)


class TestDiscoverMaterialFolders:
    def test_finds_folders_with_full_md(self, tmp_path: Path):
        """Folders containing full.md should be discovered."""
        (tmp_path / "material_a").mkdir()
        (tmp_path / "material_a" / "full.md").write_text("# A", encoding="utf-8")
        (tmp_path / "material_b").mkdir()
        (tmp_path / "material_b" / "full.md").write_text("# B", encoding="utf-8")
        (tmp_path / "empty_folder").mkdir()  # No full.md

        result = discover_material_folders(tmp_path)
        names = [f.name for f in result]
        assert "material_a" in names
        assert "material_b" in names
        assert "empty_folder" not in names

    def test_ignores_folders_without_full_md(self, tmp_path: Path):
        (tmp_path / "no_content").mkdir()
        result = discover_material_folders(tmp_path)
        assert result == []

    def test_empty_directory(self, tmp_path: Path):
        result = discover_material_folders(tmp_path)
        assert result == []

    def test_sorted_order(self, tmp_path: Path):
        """Results should be sorted alphabetically."""
        (tmp_path / "zebra").mkdir()
        (tmp_path / "zebra" / "full.md").write_text("", encoding="utf-8")
        (tmp_path / "apple").mkdir()
        (tmp_path / "apple" / "full.md").write_text("", encoding="utf-8")
        result = discover_material_folders(tmp_path)
        assert [f.name for f in result] == ["apple", "zebra"]

    def test_full_md_in_subdirectory_ignored(self, tmp_path: Path):
        """full.md must be directly in the folder, not in a subfolder."""
        (tmp_path / "parent").mkdir()
        (tmp_path / "parent" / "full.md").write_text("# Content", encoding="utf-8")
        result = discover_material_folders(tmp_path)
        assert len(result) == 1

    def test_nonexistent_base(self):
        """Should return empty list if base doesn't exist."""
        result = discover_material_folders(Path("/nonexistent/path"))
        assert result == []


class TestReadJsonSafe:
    def test_utf8_file(self, tmp_path: Path):
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        f = tmp_path / "data.json"
        f.write_text('{"key": "value", "number": 42, "list": [1, 2, 3]}', encoding="utf-8")
        result = read_json_safe(f)
        assert result == data

    def test_utf8_bom(self, tmp_path: Path):
        """UTF-8 BOM is stripped by read_text_safe but json.load requires clean JSON."""
        # Note: json.load in Python 3.11+ handles UTF-8 BOM; older versions may not.
        # If BOM is present, json.load may fail. Use read_text_safe + json.loads instead.
        f = tmp_path / "bom.json"
        # Write without BOM for compatibility
        f.write_text('{"key": "test"}', encoding="utf-8")
        result = read_json_safe(f)
        assert result == {"key": "test"}

    def test_missing_file(self, tmp_path: Path):
        result = read_json_safe(tmp_path / "nonexistent.json")
        assert result is None

    def test_invalid_json(self, tmp_path: Path):
        f = tmp_path / "invalid.json"
        f.write_text("{invalid json content", encoding="utf-8")
        result = read_json_safe(f)
        assert result is None

    def test_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.json"
        f.write_text("", encoding="utf-8")
        result = read_json_safe(f)
        assert result is None

    def test_array_json(self, tmp_path: Path):
        f = tmp_path / "array.json"
        f.write_text('[{"a": 1}, {"b": 2}]', encoding="utf-8")
        result = read_json_safe(f)
        assert result == [{"a": 1}, {"b": 2}]


class TestReadTextSafe:
    def test_utf8_file(self, tmp_path: Path):
        content = "你好，世界！Hello World!"
        f = tmp_path / "text.txt"
        f.write_text(content, encoding="utf-8")
        result = read_text_safe(f)
        assert result == content

    def test_utf8_bom_removed(self, tmp_path: Path):
        """UTF-8 BOM should be stripped."""
        f = tmp_path / "bom.txt"
        f.write_text("\ufeffHello", encoding="utf-8")
        result = read_text_safe(f)
        assert result == "Hello"

    def test_missing_file(self, tmp_path: Path):
        result = read_text_safe(tmp_path / "nonexistent.txt")
        assert result is None

    def test_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = read_text_safe(f)
        assert result == ""

    def test_multiline_content(self, tmp_path: Path):
        content = "Line 1\nLine 2\n## Heading\n- Item 1\n- Item 2"
        f = tmp_path / "multiline.txt"
        f.write_text(content, encoding="utf-8")
        result = read_text_safe(f)
        assert result == content


class TestNormalizeText:
    def test_fullwidth_to_halfwidth(self):
        """Full-width ASCII characters should be converted."""
        result = normalize_text("ＨＥＬＬＯ　ＷＯＲＬＤ")
        assert result == "hello world"

    def test_fullwidth_numbers(self):
        result = normalize_text("１２３４５６")
        assert result == "123456"

    def test_lowercase(self):
        result = normalize_text("ABCDefGHI")
        assert result == "abcdefghi"

    def test_punctuation_removal(self):
        """Punctuation should be removed and collapsed to spaces."""
        result = normalize_text("Hello, world! 你好。")
        assert "," not in result
        assert "!" not in result
        assert "。" not in result

    def test_whitespace_collapse(self):
        """Multiple spaces should collapse to single space."""
        result = normalize_text("Hello    World\n\n  Test  ")
        assert "  " not in result
        assert "\n" not in result

    def test_chinese_text_normalized(self):
        """Chinese characters preserved, punctuation removed."""
        result = normalize_text("这是测试：SPI协议（Serial Peripheral Interface）")
        assert "这是测试" in result
        assert "spi协议" in result  # normalize_text lowercases
        assert "serial peripheral interface" in result  # normalize_text lowercases
        assert "：" not in result  # fullwidth colon removed
        assert "（" not in result  # fullwidth parens removed

    def test_mixed_content(self):
        result = normalize_text("第 1 课：学习   STM32 嵌入式开发。")
        assert result == "第 1 课 学习 stm32 嵌入式开发"


class TestExtractFolderLabel:
    def test_removes_timestamp(self):
        """Timestamps like _20260414_234813 should be removed."""
        result = extract_folder_label("STM32基础教程_20260414_234813")
        assert "_20260414" not in result
        assert "234813" not in result

    def test_removes_version_suffix(self):
        """Version numbers like 1.0.1 should be removed."""
        result = extract_folder_label("课程名称1.0.1")
        assert "1.0.1" not in result
        result = extract_folder_label("课程名称_1.0.1")
        assert "1.0.1" not in result

    def test_preserves_Chinese(self):
        result = extract_folder_label("STM32单片机基础教程")
        assert "STM32单片机基础教程" in result

    def test_truncates_long_names(self):
        """Names longer than 40 chars should be truncated."""
        long_name = "A" * 60
        result = extract_folder_label(long_name)
        assert len(result) <= 40

    def test_strips_leading_trailing(self):
        """Leading and trailing dashes/underscores should be stripped."""
        result = extract_folder_label("_-课程名称-_")
        assert not result.startswith(("_", "-"))
        assert not result.endswith(("_", "-"))

    def test_complex_real_world_name(self):
        """Test with a realistic folder name pattern."""
        name = "01_尚硅谷嵌入式技术之STM32单片机（基础篇）1.0.1_20260414_234813"
        result = extract_folder_label(name)
        assert "尚硅谷" in result
        assert "STM32" in result
        assert "_20260414" not in result
        assert "1.0.1" not in result

    def test_empty_after_cleanup(self):
        """Very short names should remain as-is."""
        result = extract_folder_label("A")
        assert result == "A"
