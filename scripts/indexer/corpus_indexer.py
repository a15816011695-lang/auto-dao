"""Shared corpus index builder — cross-material concept matching."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import jieba
    import Levenshtein
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

from indexer.utils import (
    discover_material_folders,
    read_text_safe,
    read_json_safe,
    normalize_text,
    extract_folder_label,
)
from indexer.md_parser import extract_headings, extract_image_refs, Heading


# Chinese stopwords to filter out
STOPWORDS = {"的", "是", "在", "了", "和", "与", "或", "以及", "为", "与", "其",
             "本", "该", "各", "个", "等", "之", "以", "于", "对", "中", "上",
             "下", "可", "能", "将", "要", "会", "有", "从", "到", "也", "而",
             "又", "但", "则", "所", "被", "比", "如", "当", "由", "此", "并"}


@dataclass
class MaterialEntry:
    folder: Path
    label: str
    headings: list[Heading]
    heading_texts: list[str]      # Raw heading texts
    keywords_per_heading: dict[str, list[str]]  # heading_text -> [keyword, ...]
    image_hashes: set[str]


@dataclass
class ConceptGroup:
    topic: str
    variations: list[str] = field(default_factory=list)
    cross_refs: dict[str, dict] = field(default_factory=dict)  # label -> data


def _tokenize(text: str) -> list[str]:
    """Tokenize Chinese text using jieba, filter stopwords."""
    if not JIEBA_AVAILABLE:
        # Fallback: simple character-based splitting
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text)
        return [t for t in tokens if len(t) >= 2 and t not in STOPWORDS]
    tokens = jieba.cut(text)
    return [t.strip() for t in tokens
            if len(t.strip()) >= 2 and t.strip() not in STOPWORDS
            and re.search(r"[\u4e00-\u9fff]|[a-zA-Z]", t)]


def _heading_keywords(heading: Heading) -> list[str]:
    """Extract keywords from a heading using jieba."""
    # Remove numbering (e.g. "1.1 ", "1) ", "（1）")
    text = re.sub(r"^[\d\.（()）\u4e00-\u9fff]+\s*", "", heading.text)
    return _tokenize(text)


def _compute_similarity(text1: str, text2: str) -> float:
    """Compute similarity between two text strings using Levenshtein."""
    n1, n2 = len(text1), len(text2)
    if n1 == 0 and n2 == 0:
        return 1.0
    if n1 == 0 or n2 == 0:
        return 0.0
    if not JIEBA_AVAILABLE:
        # Fallback: simple character overlap
        set1, set2 = set(text1), set(text2)
        return len(set1 & set2) / len(set1 | set2)
    # Use Levenshtein ratio
    return Levenshtein.ratio(text1, text2)


def _keywords_overlap(kw1: list[str], kw2: list[str]) -> float:
    """Compute keyword overlap between two keyword lists."""
    if not kw1 or not kw2:
        return 0.0
    s1, s2 = set(kw1), set(kw2)
    return len(s1 & s2) / len(s1 | s2)


def build_material_entries(folders: list[Path]) -> list[MaterialEntry]:
    """Build MaterialEntry for each folder."""
    entries = []
    for folder in folders:
        full_md = folder / "full.md"
        text = read_text_safe(full_md) or ""

        headings = extract_headings(text)
        # Keep only H1 and H2
        headings = [h for h in headings if h.level in (1, 2)]

        heading_texts = [h.text for h in headings]
        keywords_per_heading = {h.text: _heading_keywords(h) for h in headings}

        # Collect image hashes referenced in this material
        image_refs = extract_image_refs(text)
        image_hashes = {ref.hash for ref in image_refs}

        entries.append(MaterialEntry(
            folder=folder,
            label=extract_folder_label(folder.name),
            headings=headings,
            heading_texts=heading_texts,
            keywords_per_heading=keywords_per_heading,
            image_hashes=image_hashes,
        ))

    return entries


def _find_images_for_heading(heading_text: str, folder: Path) -> list[str]:
    """Find image hashes that appear near a heading in the material."""
    full_md = folder / "full.md"
    text = read_text_safe(full_md) or ""
    refs = extract_image_refs(text)

    # Find refs whose context mentions heading keywords
    heading_kw = set(_tokenize(heading_text))
    matched = []
    for ref in refs:
        ctx = ref.context_before + " " + ref.context_after
        ctx_kw = set(_tokenize(ctx))
        if heading_kw & ctx_kw:  # intersection
            matched.append(ref.hash)
    return matched[:3]  # Max 3 images per heading


def match_concepts(entries: list[MaterialEntry], sim_threshold: float = 0.55) -> list[ConceptGroup]:
    """Match concepts across materials and build groups."""
    # Build a flat list of (entry_label, heading_text, heading_obj, keywords, images)
    all_items: list[dict] = []
    for entry in entries:
        for h in entry.headings:
            images = _find_images_for_heading(h.text, entry.folder)
            all_items.append({
                "label": entry.label,
                "heading": h.text,
                "heading_obj": h,
                "keywords": entry.keywords_per_heading.get(h.text, []),
                "images": images,
            })

    # Cluster items by similarity
    groups: list[ConceptGroup] = []
    used = set()

    for i, item_i in enumerate(all_items):
        if i in used:
            continue

        # Start a new group
        topic = item_i["heading"]
        group = ConceptGroup(topic=topic, variations=[item_i["heading"]])

        cross_ref = {
            item_i["label"]: {
                "headings": [item_i["heading"]],
                "keywords": item_i["keywords"],
                "weight": (3 if item_i["heading_obj"].level == 1 else 2),
                "images": item_i["images"],
            }
        }
        used.add(i)

        # Find matches in other items
        for j, item_j in enumerate(all_items):
            if j in used or item_j["label"] == item_i["label"]:
                continue

            # Check: same keywords overlap OR high text similarity
            kw_sim = _keywords_overlap(item_i["keywords"], item_j["keywords"])
            text_sim = _compute_similarity(item_i["heading"], item_j["heading"])

            if kw_sim >= 0.35 or text_sim >= sim_threshold:
                if item_j["heading"] not in group.variations:
                    group.variations.append(item_j["heading"])

                if item_j["label"] not in cross_ref:
                    cross_ref[item_j["label"]] = {
                        "headings": [],
                        "keywords": item_j["keywords"],
                        "weight": 0,
                        "images": item_j["images"],
                    }

                cross_ref[item_j["label"]]["headings"].append(item_j["heading"])
                cross_ref[item_j["label"]]["weight"] += (
                    3 if item_j["heading_obj"].level == 1 else 2
                )
                used.add(j)

        group.cross_refs = cross_ref
        groups.append(group)

    return groups


def build_shared_corpus(folders: list[Path]) -> dict:
    """Build the complete shared corpus index."""
    entries = build_material_entries(folders)
    groups = match_concepts(entries)

    # Sort groups by number of materials they appear in (most cross-referenced first)
    groups.sort(key=lambda g: len(g.cross_refs), reverse=True)

    return {
        "_meta": {
            "generated": __import__("datetime").date.today().isoformat(),
            "sources": [e.label for e in entries],
            "total_concepts": sum(len(e.headings) for e in entries),
            "cross_material_concepts": len([g for g in groups if len(g.cross_refs) > 1]),
        },
        "groups": [
            {
                "topic": g.topic,
                "variations": g.variations,
                "cross_refs": g.cross_refs,
            }
            for g in groups
        ],
    }
