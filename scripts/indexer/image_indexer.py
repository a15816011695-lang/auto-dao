"""Image index builder — extract descriptions and tags from markdown context."""
from __future__ import annotations

import os
import re
import json as _json
from pathlib import Path
from typing import Optional

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

from .utils import read_text_safe, normalize_text
from .md_parser import extract_headings, extract_image_refs, Heading


# Same STOPWORDS from corpus_indexer
STOPWORDS = {"的", "是", "在", "了", "和", "与", "或", "以及", "为", "其",
             "本", "该", "各", "个", "等", "之", "以", "于", "对", "中", "上",
             "下", "可", "能", "将", "要", "会", "从", "到", "也", "而",
             "又", "但", "则", "所", "被", "比", "如", "当", "由", "此", "并"}


def _tokenize(text: str) -> list[str]:
    if not JIEBA_AVAILABLE:
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text)
        return [t for t in tokens if len(t) >= 2 and t not in STOPWORDS]
    tokens = jieba.cut(text)
    return [t.strip() for t in tokens
            if len(t.strip()) >= 2 and t.strip() not in STOPWORDS
            and re.search(r"[\u4e00-\u9fff]|[a-zA-Z]", t)]


def _extract_tags(context: str) -> list[str]:
    """Extract technical keywords as tags from context."""
    tokens = _tokenize(context)
    # Deduplicate while preserving order
    seen = set()
    tags = []
    for t in tokens:
        if t not in seen and len(t) >= 2:
            seen.add(t)
            tags.append(t)
    return tags[:15]  # Max 15 tags per image


def _find_nearest_heading(line_no: int, headings: list[Heading]) -> Optional[Heading]:
    """Find the nearest heading before the given line number."""
    # headings don't have line numbers, so we approximate by
    # finding the last H1/H2 in the reversed list (search backwards from end)
    candidates = [h for h in headings if h.level in (1, 2)]
    # Since we don't have line numbers in Heading, return the last H1 or H2
    return candidates[-1] if candidates else None


def _build_heading_chain(line_no: int, headings: list[Heading]) -> list[str]:
    """Build heading chain (H1 -> H2 -> ...) up to the given line."""
    chain = []
    for h in headings:
        if h.level in (1, 2) and len(chain) < 5:
            chain.append(h.text)
    return chain


def _generate_description(image_ref, headings: list[Heading]) -> str:
    """Generate 1-3 sentence description from context.

    Algorithm:
    1. Find nearest H1/H2 heading
    2. Extract first meaningful sentence from context_before
    3. Concatenate: "{heading}。{first_sentence}"
    4. Truncate at 50 chars
    """
    # Find nearest heading
    nearest_h = None
    for h in reversed(headings):
        if h.level in (1, 2):
            nearest_h = h
            break

    heading_part = nearest_h.text if nearest_h else ""

    # Extract first sentence from context_before
    sentence = ""
    ctx = image_ref.context_before
    # Find first complete sentence (ends with Chinese or English punctuation)
    for match in re.finditer(r"[^。！？.!?]+[。！？.!?]?", ctx):
        sentence = match.group().strip()
        if len(sentence) >= 5:
            break

    # Concatenate
    if heading_part and sentence:
        desc = f"{heading_part}。{sentence}"
    elif heading_part:
        desc = heading_part
    elif sentence:
        desc = sentence
    else:
        desc = "图片"

    # Truncate at 50 chars
    if len(desc) > 50:
        desc = desc[:50].rstrip("，、的了是在和")
    return desc


def build_image_index(folder: Path) -> dict:
    """Build image index for a single material folder."""
    full_md = folder / "full.md"
    images_dir = folder / "images"
    layout_json = folder / "layout.json"

    text = read_text_safe(full_md) or ""
    headings = extract_headings(text)
    image_refs = extract_image_refs(text)

    # Load layout for page estimation (best effort)
    layout = None
    if layout_json.exists():
        from .utils import read_json_safe
        layout = read_json_safe(layout_json)

    result_images = []
    for ref in image_refs:
        # Check if image file exists
        img_path = images_dir / f"{ref.hash}.jpg"
        if img_path.exists():
            rel_path = f"{folder.name}/images/{ref.hash}.jpg"
            size_bytes = img_path.stat().st_size
        else:
            rel_path = ""
            size_bytes = 0

        description = _generate_description(ref, headings)
        tags = _extract_tags(ref.context_before + " " + ref.context_after)
        heading_chain = _build_heading_chain(ref.line_no, headings)

        result_images.append({
            "filename": f"{ref.hash}.jpg",
            "path": rel_path,
            "description": description,
            "tags": tags,
            "headings": heading_chain,
            "page_approx": None,  # layout.json page estimation is complex, set to null for now
            "size_bytes": size_bytes,
        })

    return {
        "_meta": {
            "source": folder.name,
            "total_images": len(result_images),
            "generated": __import__("datetime").date.today().isoformat(),
        },
        "images": result_images,
    }
