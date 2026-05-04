from __future__ import annotations

from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIB_ROOT = PROJECT_ROOT / "lib"


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def list_canon_markdown_files(lib_root: Path = LIB_ROOT) -> List[Path]:
    if not lib_root.exists():
        return []

    return sorted(
        path
        for path in lib_root.rglob("*.md")
        if path.is_file()
    )


def read_canon_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(str(path))

    if path.suffix.lower() != ".md":
        raise ValueError("Only markdown canon files may be read.")

    return {
        "path": str(path),
        "content": _safe_read_text(path),
    }


def read_all_canon(lib_root: Path = LIB_ROOT) -> List[Dict[str, str]]:
    return [
        read_canon_file(path)
        for path in list_canon_markdown_files(lib_root)
    ]