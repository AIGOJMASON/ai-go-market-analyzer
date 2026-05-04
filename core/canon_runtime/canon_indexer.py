from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .canon_reader import LIB_ROOT, list_canon_markdown_files


LAYER_KEYWORDS = (
    "layer",
    "policy",
    "contract",
    "interface",
    "definition",
    "standard",
)


def _relative_to_lib(path: Path) -> str:
    try:
        return str(path.relative_to(LIB_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _split_path_parts(rel_path: str) -> List[str]:
    return rel_path.replace("\\", "/").split("/")


def _is_layer_file(path: Path) -> bool:
    name = path.name.lower()

    return any(keyword in name for keyword in LAYER_KEYWORDS)


def _layer_key(path: Path) -> str:
    name = path.name.lower().replace(".md", "")

    for keyword in LAYER_KEYWORDS:
        if keyword in name:
            return keyword

    return "other"


def build_canon_index() -> Dict[str, Any]:
    files = list_canon_markdown_files()

    by_domain: Dict[str, List[str]] = {}
    by_layer: Dict[str, List[str]] = {}
    all_files: List[str] = []

    for path in files:
        rel_path = _relative_to_lib(path)
        parts = _split_path_parts(rel_path)

        all_files.append(rel_path)

        if parts:
            domain = parts[0]
            by_domain.setdefault(domain, []).append(rel_path)

        if _is_layer_file(path):
            key = _layer_key(path)
            by_layer.setdefault(key, []).append(rel_path)

    return {
        "by_domain": dict(sorted(by_domain.items())),
        "by_layer": dict(sorted(by_layer.items())),
        "all_files": sorted(all_files),
    }