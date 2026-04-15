"""Utility functions for the indexer."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional


def discover_material_folders(base: Path) -> list[Path]:
    """Discover all material folders under base (each has full.md)."""
    folders = []
    if not base.exists():
        return folders
    for item in sorted(base.iterdir()):
        if item.is_dir() and (item / "full.md").exists():
            folders.append(item)
    return folders


def read_json_safe(path: Path) -> Optional[dict | list]:
    """Read JSON with multiple encoding fallbacks."""
    if not path.exists():
        return None
    for enc in ("utf-8", "gbk", "gb2312", "gb18030", "latin1"):
        try:
            with open(path, encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None


def read_text_safe(path: Path) -> Optional[str]:
    """Read text file with multiple encoding fallbacks. Handles UTF-8 BOM."""
    if not path.exists():
        return None
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312", "latin1"):
        try:
            with open(path, encoding=enc) as f:
                content = f.read()
                # utf-8-sig already stripped BOM; for utf-8, strip it manually
                if enc == "utf-8" and content.startswith("\ufeff"):
                    content = content[1:]
                return content
        except UnicodeDecodeError:
            continue
    return None


def normalize_text(text: str) -> str:
    """Normalize text: full-width to half-width, lowercase, remove punctuation."""
    # Full-width to half-width
    s = ""
    for ch in text:
        code = ord(ch)
        if 0xFF01 <= code <= 0xFF5E:
            code -= 0xFEE0
        elif code == 0x3000:
            code = 0x0020
        s += chr(code)
    # Lowercase
    s = s.lower()
    # Remove punctuation: ASCII punctuation + full-width (U+FF00-U+FFEF) + CJK (U+3000-U+303F)
    s = re.sub(r"[\s\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e\uff00-\uffef\u3000-\u303f]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_folder_label(folder_name: str) -> str:
    """Extract a short display label from folder name.

    e.g. '01_尚硅谷嵌入式技术之STM32单片机（基础篇）1.0.1_20260414_234813'
        -> '01_尚硅谷STM32基础篇'
    """
    # Remove timestamp suffix
    name = re.sub(r"_\d{8}_\d{6}$", "", folder_name)
    # Remove version suffix
    name = re.sub(r"[\d]+\.[\d]+\.[\d]+_?$", "", name)
    # Truncate long names
    if len(name) > 40:
        name = name[:40]
    return name.strip("_-")
