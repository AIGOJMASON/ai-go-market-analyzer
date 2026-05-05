from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .canon_indexer import build_canon_index
from .canon_reader import LIB_ROOT, read_canon_file


def _resolve_paths(file_paths: List[str]) -> List[Path]:
    return [LIB_ROOT / path for path in file_paths]


def build_domain_context(domain: str) -> Dict[str, object]:
    index = build_canon_index()
    files = index["by_domain"].get(domain, [])

    resolved = _resolve_paths(files)

    return {
        "domain": domain,
        "file_count": len(resolved),
        "files": [str(p) for p in resolved],
        "documents": [read_canon_file(p) for p in resolved],
    }


def build_layer_context(layer_name: str) -> Dict[str, object]:
    index = build_canon_index()
    files = index["by_layer"].get(layer_name.lower(), [])

    resolved = _resolve_paths(files)

    return {
        "layer": layer_name,
        "file_count": len(resolved),
        "files": [str(p) for p in resolved],
        "documents": [read_canon_file(p) for p in resolved],
    }


def build_full_canon_context(limit: Optional[int] = None) -> Dict[str, object]:
    index = build_canon_index()
    files = index["all_files"]

    if limit is not None:
        files = files[:limit]

    resolved = _resolve_paths(files)

    return {
        "total_files": len(resolved),
        "files": [str(p) for p in resolved],
        "documents": [read_canon_file(p) for p in resolved],
    }