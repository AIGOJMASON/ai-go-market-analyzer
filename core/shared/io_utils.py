"""
AI_GO/core/shared/io_utils.py

File and JSON input/output helpers for AI_GO.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_parent_dir(path: Path) -> None:
    """
    Ensure the parent directory for a path exists.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    """
    Read a text file and return its contents.
    """
    return Path(path).read_text(encoding=encoding)


def write_text_file(path: str | Path, content: str, encoding: str = "utf-8") -> Path:
    """
    Write text content to a file.
    """
    target = Path(path)
    ensure_parent_dir(target)
    target.write_text(content, encoding=encoding)
    return target


def read_json_file(path: str | Path) -> Any:
    """
    Read JSON content from a file and return the parsed object.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_file(path: str | Path, payload: Any, *, indent: int = 2) -> Path:
    """
    Write a JSON-serializable payload to a file.
    """
    target = Path(path)
    ensure_parent_dir(target)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=indent)
        handle.write("\n")
    return target