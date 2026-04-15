"""Tests for .claude/skills/everything-to-markdown/scripts/convert_to_markdown.py"""

import sys
import os
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / ".claude" / "skills" / "everything-to-markdown" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import convert_to_markdown


class TestIsUrl:
    def test_valid_http_url(self):
        assert convert_to_markdown.is_url("https://example.com/file.pdf")
        assert convert_to_markdown.is_url("http://example.com/file.pdf")

    def test_valid_url_with_path(self):
        assert convert_to_markdown.is_url("https://example.com/path/to/doc.pdf")

    def test_invalid_no_scheme(self):
        assert not convert_to_markdown.is_url("example.com/file.pdf")

    def test_invalid_no_netloc(self):
        assert not convert_to_markdown.is_url("file:///path/to/file.pdf")

    def test_empty_string(self):
        assert not convert_to_markdown.is_url("")

    def test_local_path(self):
        assert not convert_to_markdown.is_url("./documents/report.pdf")
        assert not convert_to_markdown.is_url("/home/user/doc.pdf")
        assert not convert_to_markdown.is_url("C:\\Users\\doc.pdf")


class TestGetFileExtension:
    def test_local_pdf(self):
        assert convert_to_markdown.get_file_extension("document.pdf") == "pdf"
        assert convert_to_markdown.get_file_extension("/path/to/document.PDF") == "pdf"

    def test_local_docx(self):
        assert convert_to_markdown.get_file_extension("report.docx") == "docx"

    def test_url_extension(self):
        assert convert_to_markdown.get_file_extension("https://example.com/file.pdf") == "pdf"
        assert convert_to_markdown.get_file_extension("https://example.com/path?query=1") == ""

    def test_no_extension(self):
        assert convert_to_markdown.get_file_extension("Makefile") == ""
        assert convert_to_markdown.get_file_extension("/path/to/README") == ""

    def test_double_extension(self):
        assert convert_to_markdown.get_file_extension("file.tar.gz") == "gz"


class TestCheckFileSize:
    def test_small_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 1024)  # 1 KB
            f.flush()
            temp_path = f.name
        try:
            convert_to_markdown._check_file_size(temp_path)  # Should not raise
        finally:
            os.unlink(temp_path)

    def test_oversized_file(self):
        # Create a temp file larger than MAX_FILE_SIZE_MB
        # We'll mock the size by patching os.path.getsize
        import convert_to_markdown
        original_getsize = os.path.getsize

        def fake_getsize(path):
            return (convert_to_markdown.MAX_FILE_SIZE_MB + 10) * 1024 * 1024

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            os.path.getsize = fake_getsize
            try:
                convert_to_markdown._check_file_size(temp_path)
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "超过" in str(e)
        finally:
            os.path.getsize = original_getsize
            os.unlink(temp_path)


class TestGetApiKey:
    def test_missing_env_and_file(self, monkeypatch):
        """No .env file and no env var → ValueError"""
        monkeypatch.delenv("MINERU_API_KEY", raising=False)
        monkeypatch.chdir("/")  # Ensure not in project root
        try:
            convert_to_markdown.get_api_key(project_root="/nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "MINERU_API_KEY" in str(e)

    def test_invalid_placeholder(self, monkeypatch):
        """API key set to placeholder value → ValueError"""
        monkeypatch.setenv("MINERU_API_KEY", "TODO")
        monkeypatch.chdir("/")
        try:
            convert_to_markdown.get_api_key(project_root="/nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "无效" in str(e)
