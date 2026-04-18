#!/usr/bin/env python
"""Sync source material images and index into a learning session.

Given:
    - processed_path: MinerU converted material dir (tmp/converted/{material}_{ts}/)
    - session_dir: learning session dir (learning-history/{topic}_{ts}/)

Do:
    1. Locate the pre-built global image index at
       tmp/converted/index/{label}/image_index.json (or optionally auto-build it).
    2. Copy the index to {session_dir}/image_index.json with `path` fields rewritten
       from "{material_folder}/images/{hash}.jpg" to "images/{hash}.jpg" so that
       lessons can reference images via `../images/{hash}.jpg`.
    3. Copy all images from {processed_path}/images/ to {session_dir}/images/.

This gives each learning session a self-contained `images/` directory plus a
session-local `image_index.json` that lesson generation can consult (per
SKILL.md §4.2.1 decision tree) to prefer source-material images over
AI-generated DrawIO figures.

Usage:
    py scripts/indexer/sync_images_to_session.py <processed_path> <session_dir>

Example:
    py scripts/indexer/sync_images_to_session.py \
        tmp/converted/04-STM32F103HAL库开发_20260413_094457 \
        learning-history/003_stm32f103-hal_2026-04-13-09-45
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Make scripts/ importable so we can reuse indexer utilities.
_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from indexer.utils import extract_folder_label, read_json_safe  # noqa: E402


def find_source_index(processed_path: Path) -> Optional[Path]:
    """Locate the pre-built image_index.json for this material.

    Searches under tmp/converted/index/{label}/image_index.json, where
    {label} is the shortened folder name (timestamp and version stripped).
    Returns None if the index does not exist yet.
    """
    label = extract_folder_label(processed_path.name)
    candidate = processed_path.parent / "index" / label / "image_index.json"
    return candidate if candidate.exists() else None


def build_global_index(project_root: Path) -> None:
    """Invoke scripts/indexer/build_corpus_index.py to (re)build all indexes."""
    build_script = project_root / "scripts" / "indexer" / "build_corpus_index.py"
    if not build_script.exists():
        raise FileNotFoundError(f"build_corpus_index.py not found: {build_script}")
    subprocess.run(
        [sys.executable, str(build_script)],
        cwd=str(project_root),
        check=True,
    )


def rewrite_paths_for_session(index: dict, material_folder_name: str) -> dict:
    """Rewrite `path` from '{material_folder}/images/x.jpg' to 'images/x.jpg'.

    The original index stores paths relative to tmp/converted/, so each entry
    looks like `04-STM32F103HAL库开发_20260413_094457/images/abc.jpg`. After
    rewriting they become `images/abc.jpg`, valid relative to the session root.

    Entries whose path doesn't start with the expected prefix are left
    untouched so legitimate external references (if any) survive.
    """
    prefix = material_folder_name.rstrip("/") + "/"
    new_images: list[dict] = []
    for img in index.get("images", []):
        new_img = dict(img)
        old_path = img.get("path", "")
        if old_path.startswith(prefix):
            new_img["path"] = old_path[len(prefix):]
        new_images.append(new_img)

    new_index = dict(index)
    new_index["images"] = new_images

    new_meta = dict(index.get("_meta", {}))
    new_meta["session_local"] = True
    new_meta["source_material_folder"] = material_folder_name
    new_index["_meta"] = new_meta
    return new_index


def copy_images(source_images: Path, target_images: Path) -> tuple[int, int]:
    """Copy every file from source to target; skip if identically sized already.

    Returns (copied, skipped). Skipped entries are treated as already-synced
    to make this function idempotent and cheap to re-run.
    """
    if not source_images.is_dir():
        return 0, 0

    target_images.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    for img in sorted(source_images.iterdir()):
        if not img.is_file():
            continue
        dst = target_images / img.name
        if dst.exists() and dst.stat().st_size == img.stat().st_size:
            skipped += 1
            continue
        shutil.copy2(img, dst)
        copied += 1
    return copied, skipped


def sync(
    processed_path: Path,
    session_dir: Path,
    auto_build: bool = True,
    project_root: Optional[Path] = None,
) -> dict:
    """Main entry. Returns a summary dict for callers (CLI and tests)."""
    processed_path = processed_path.resolve()
    session_dir = session_dir.resolve()

    if not processed_path.is_dir():
        raise FileNotFoundError(f"processed_path not found: {processed_path}")
    if not session_dir.is_dir():
        raise FileNotFoundError(f"session_dir not found: {session_dir}")

    # 1. Locate (or build) the source index.
    source_index_path = find_source_index(processed_path)
    if source_index_path is None:
        if auto_build:
            if project_root is None:
                project_root = processed_path.parent.parent  # tmp/converted -> project root
            build_global_index(project_root)
            source_index_path = find_source_index(processed_path)
        if source_index_path is None:
            raise FileNotFoundError(
                f"image_index.json not found for {processed_path.name}; "
                f"run `py scripts/indexer/build_corpus_index.py` first"
            )

    # 2. Read and rewrite paths for session-local use.
    source_index = read_json_safe(source_index_path)
    if source_index is None:
        raise RuntimeError(f"Failed to read index: {source_index_path}")

    session_index = rewrite_paths_for_session(source_index, processed_path.name)

    target_index_path = session_dir / "image_index.json"
    target_index_path.write_text(
        json.dumps(session_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 3. Copy images alongside the index.
    source_images = processed_path / "images"
    target_images = session_dir / "images"
    copied, skipped = copy_images(source_images, target_images)

    return {
        "source_index_path": str(source_index_path),
        "session_index_path": str(target_index_path),
        "images_dir": str(target_images),
        "total_in_index": len(session_index.get("images", [])),
        "copied": copied,
        "skipped": skipped,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "processed_path",
        help="MinerU converted material dir (e.g. tmp/converted/{material}_{ts}/)",
    )
    parser.add_argument(
        "session_dir",
        help="Learning session dir (e.g. learning-history/{topic}_{ts}/)",
    )
    parser.add_argument(
        "--no-auto-build",
        action="store_true",
        help="Do not rebuild the global index if missing (default: auto-build)",
    )
    args = parser.parse_args()

    try:
        result = sync(
            Path(args.processed_path),
            Path(args.session_dir),
            auto_build=not args.no_auto_build,
        )
    except Exception as exc:  # noqa: BLE001 - surface any error to CLI
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[ok] session index: {result['session_index_path']}")
    print(f"[ok] images: {result['copied']} copied, {result['skipped']} skipped")
    print(f"[ok] total entries in index: {result['total_in_index']}")


if __name__ == "__main__":
    main()
