"""Tests for the corpus indexer."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from indexer.utils import normalize_text, extract_folder_label
from indexer.md_parser import extract_headings, extract_image_refs


def test_normalize_text():
    assert normalize_text("ABC") == "abc"
    # Chinese punctuation converted to ASCII then removed -> empty
    assert normalize_text("，。、") == ""
    # Chinese full-width to half-width
    assert normalize_text("ＡＢＣ") == "abc"
    print("normalize_text: PASS")


def test_extract_headings():
    text = """# 第一章 ARM基础
## 1.1 ARM概述
### 什么是ARM
## 1.2 Cortex-M3
# 第二章 STM32
"""
    headings = extract_headings(text)
    assert len(headings) == 5
    assert headings[0].text == "第一章 ARM基础"
    assert headings[0].level == 1
    assert headings[1].text == "1.1 ARM概述"
    assert headings[1].level == 2
    print("extract_headings: PASS")


def test_extract_image_refs():
    text = """# 第一章 ARM

这是关于ARM的描述文字。

![](images/de2fcdfb2a5129ed8f0022234886710648ed040cf9e0cce7262cf1cba49e9d85.jpg)

## 1.2 STM32

![](images/560df87f08fd0ac1a8761f33652199d32995a76174ee351703b4fda83dc95ff3.jpg)
"""
    refs = extract_image_refs(text)
    assert len(refs) == 2
    assert refs[0].hash == "de2fcdfb2a5129ed8f0022234886710648ed040cf9e0cce7262cf1cba49e9d85"
    print("extract_image_refs: PASS")


def test_extract_folder_label():
    label = extract_folder_label("01_尚硅谷嵌入式技术之STM32单片机（基础篇）1.0.1_20260414_234813")
    assert len(label) <= 50
    print(f"extract_folder_label: '{label}' -> PASS")


def test_end_to_end():
    """Run the full indexer on one material folder."""
    base = Path(__file__).parent.parent.parent / "tmp" / "converted"
    from indexer.corpus_indexer import build_shared_corpus
    from indexer.image_indexer import build_image_index
    from indexer.utils import discover_material_folders

    folders = discover_material_folders(base)
    if not folders:
        print("SKIP (no folders found)")
        return

    # Build corpus
    corpus = build_shared_corpus(folders[:1])
    assert "_meta" in corpus
    assert "groups" in corpus
    print(f"end_to_end corpus: {len(corpus['groups'])} groups -> PASS")

    # Build image index
    img_idx = build_image_index(folders[0])
    assert "_meta" in img_idx
    assert "images" in img_idx
    print(f"end_to_end image: {img_idx['_meta']['total_images']} images -> PASS")


if __name__ == "__main__":
    test_normalize_text()
    test_extract_headings()
    test_extract_image_refs()
    test_extract_folder_label()
    test_end_to_end()
    print("\nAll tests passed!")
