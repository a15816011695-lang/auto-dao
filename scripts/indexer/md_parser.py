"""Markdown parser for the indexer."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Heading:
    level: int          # 1 for H1, 2 for H2, etc.
    text: str           # Full heading text
    raw: str            # Original line


@dataclass
class ImageRef:
    hash: str           # Image filename hash (without extension)
    line_no: int        # Line number in full.md
    context_before: str # Text before the image reference
    context_after: str  # Text after the image reference


def extract_headings(text: str) -> list[Heading]:
    """Extract all headings from markdown text."""
    headings = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if m:
            headings.append(Heading(
                level=len(m.group(1)),
                text=m.group(2).strip(),
                raw=line.strip(),
            ))
    return headings


def extract_image_refs(text: str, max_context_chars: int = 300) -> list[ImageRef]:
    """Extract all image references with surrounding context."""
    refs = []
    lines = text.splitlines()
    total = len(lines)

    for i, line in enumerate(lines):
        m = re.search(r"!\[.*?\]\((images?/([a-zA-Z0-9_-]+)\.jpg)\)", line, re.IGNORECASE)
        if not m:
            continue

        image_path = m.group(1)
        img_hash = m.group(2)

        # Collect context before (from previous line back to max chars)
        ctx_before_lines = []
        char_count = 0
        for j in range(i - 1, max(-1, i - 20), -1):
            ctx_line = lines[j].strip()
            if ctx_line:
                ctx_before_lines.append(ctx_line)
                char_count += len(ctx_line)
                if char_count >= max_context_chars:
                    break
        ctx_before_lines.reverse()
        context_before = " ".join(ctx_before_lines)

        # Collect context after
        ctx_after_lines = []
        char_count = 0
        for j in range(i + 1, min(total, i + 20)):
            ctx_line = lines[j].strip()
            if ctx_line:
                ctx_after_lines.append(ctx_line)
                char_count += len(ctx_line)
                if char_count >= max_context_chars:
                    break
        context_after = " ".join(ctx_after_lines)

        refs.append(ImageRef(
            hash=img_hash,
            line_no=i + 1,
            context_before=context_before,
            context_after=context_after,
        ))

    return refs
