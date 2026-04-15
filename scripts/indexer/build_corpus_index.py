#!/usr/bin/env python
"""Build corpus index for all converted materials in tmp/converted/.

Usage:
    py scripts/indexer/build_corpus_index.py

Output:
    tmp/converted/index/
    ├── _meta.json
    ├── shared_corpus.json
    ├── {material_folder}/image_index.json
    └── ...
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from corpus_indexer import build_shared_corpus
from image_indexer import build_image_index
from utils import discover_material_folders, extract_folder_label


def main():
    base = Path(__file__).parent.parent.parent / "tmp" / "converted"
    output = base / "index"

    print(f"Scanning: {base}")
    folders = discover_material_folders(base)
    print(f"Found {len(folders)} material folders:")
    for f in folders:
        print(f"  - {f.name}")

    if not folders:
        print("No material folders found. Exiting.")
        return

    output.mkdir(parents=True, exist_ok=True)

    # Build shared corpus
    print("\nBuilding shared corpus index...")
    corpus = build_shared_corpus(folders)
    corpus_path = output / "shared_corpus.json"
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print(f"  -> {corpus_path} ({len(corpus['groups'])} groups)")

    # Build image indexes
    print("\nBuilding image indexes...")
    total_images = 0
    for folder in folders:
        label = extract_folder_label(folder.name)
        img_dir = output / label
        img_dir.mkdir(parents=True, exist_ok=True)

        idx = build_image_index(folder)
        idx_path = img_dir / "image_index.json"
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, indent=2)
        print(f"  [{label}] {idx['_meta']['total_images']} images -> {idx_path}")
        total_images += idx["_meta"]["total_images"]

    # Write meta
    meta = {
        "generated": corpus["_meta"]["generated"],
        "sources": corpus["_meta"]["sources"],
        "shared_corpus_groups": len(corpus["groups"]),
        "cross_material_concepts": corpus["_meta"]["cross_material_concepts"],
        "total_images_indexed": total_images,
    }
    meta_path = output / "_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\nDone! Meta: {meta_path}")
    print(f"Total: {len(corpus['groups'])} concept groups, {total_images} images indexed.")


if __name__ == "__main__":
    main()