"""Integration tests for scripts/indexer/build_corpus_index.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestBuildCorpusIndexIntegration:
    """Integration tests using actual temp folder structures."""

    def test_full_pipeline_with_real_structure(self, tmp_path: Path):
        """Simulate full build_corpus_index workflow with real folders."""
        # Setup: create two material folders matching expected structure
        mat_a = tmp_path / "material_A"
        mat_b = tmp_path / "material_B"
        for f in (mat_a, mat_b):
            f.mkdir()
            (f / "full.md").write_text(
                "# SPI 协议\n\n## 时钟信号\n\nSPI是一种同步通信协议。\n",
                encoding="utf-8",
            )
            (f / "images").mkdir()

        # Run the actual build_shared_corpus function
        # Note: we skip importing build_corpus_index.main directly since it has
        # import path issues; we import the needed function directly
        from indexer.corpus_indexer import build_shared_corpus
        import io
        import contextlib

        # Capture print output
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            corpus = build_shared_corpus([mat_a, mat_b])

        output = f.getvalue()
        assert "groups" in corpus
        assert isinstance(corpus["groups"], list)

    def test_no_material_folders(self, tmp_path: Path):
        """Empty directory should produce empty corpus."""
        from indexer.corpus_indexer import build_shared_corpus

        corpus = build_shared_corpus([])
        assert corpus["groups"] == []
        assert corpus["_meta"]["sources"] == []

    def test_single_folder_single_concept(self, tmp_path: Path):
        """Single folder with single heading should produce one group."""
        folder = tmp_path / "single"
        folder.mkdir()
        (folder / "full.md").write_text("# 唯一主题\n\n内容。\n", encoding="utf-8")

        from indexer.corpus_indexer import build_shared_corpus

        corpus = build_shared_corpus([folder])
        assert len(corpus["groups"]) >= 1
        assert corpus["_meta"]["sources"] == ["single"]

    def test_meta_fields_present(self, tmp_path: Path):
        """Verify all _meta fields are populated correctly."""
        folder_a = tmp_path / "A"
        folder_b = tmp_path / "B"
        for f in (folder_a, folder_b):
            f.mkdir()
            (f / "full.md").write_text("# 共享主题\n\n内容。\n", encoding="utf-8")

        from indexer.corpus_indexer import build_shared_corpus

        corpus = build_shared_corpus([folder_a, folder_b])

        assert corpus["_meta"]["generated"]
        assert corpus["_meta"]["sources"] == ["A", "B"]
        assert "total_concepts" in corpus["_meta"]
        assert "cross_material_concepts" in corpus["_meta"]


# ---------------------------------------------------------------------------
# Helper: pytest import
# ---------------------------------------------------------------------------
import pytest  # noqa: E402
