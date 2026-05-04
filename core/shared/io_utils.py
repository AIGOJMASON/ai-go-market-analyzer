"""
AI_GO/core/shared/io_utils.py

Governed file and JSON input/output helpers for AI_GO.

Northstar Stage 6A:
All write helpers must expose mutation classification and route through
governed persistence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from AI_GO.core.governance.governed_persistence import (
    build_authority_metadata,
    governed_write_json,
    governed_write_raw_json,
)


IO_UTILS_MUTATION_CLASS = "filesystem_persistence"
IO_UTILS_PERSISTENCE_TYPE = "filesystem"
IO_UTILS_ADVISORY_ONLY = False


def _classification_block() -> Dict[str, Any]:
    return {
        "mutation_class": IO_UTILS_MUTATION_CLASS,
        "persistence_type": IO_UTILS_PERSISTENCE_TYPE,
        "advisory_only": IO_UTILS_ADVISORY_ONLY,
        "execution_allowed": False,
        "state_mutation_allowed": True,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_metadata(
    *,
    operation: str,
    target_path: str | Path,
    extra: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_authority_metadata(
        authority_id="core_shared_io_utils",
        operation=operation,
        actor="system",
        source="AI_GO.core.shared.io_utils",
        extra={
            "target_path": str(target_path),
            **dict(extra or {}),
        },
    )


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
    Write text content through governed persistence.

    Note:
    This preserves the helper API by returning Path, but the persisted content is
    now a governed payload envelope rather than an uncontrolled raw text write.
    """
    target = Path(path)

    mutation_class = IO_UTILS_MUTATION_CLASS
    persistence_type = "text_file_payload"
    advisory_only = IO_UTILS_ADVISORY_ONLY
    authority_metadata = _authority_metadata(
        operation="write_text_file",
        target_path=target,
        extra={"encoding": encoding},
    )

    payload = {
        "artifact_type": "text_file_payload",
        "content": str(content),
        "encoding": encoding,
        "classification": _classification_block(),
        "authority_metadata": authority_metadata,
        "sealed": True,
    }

    governed_write_json(
        path=target,
        payload=payload,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        advisory_only=advisory_only,
    )

    return target


def read_json_file(path: str | Path) -> Any:
    """
    Read JSON content from a file and return the parsed object.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_file(path: str | Path, payload: Any, *, indent: int = 2) -> Path:
    """
    Write a JSON-serializable payload through governed persistence.
    """
    target = Path(path)

    mutation_class = IO_UTILS_MUTATION_CLASS
    persistence_type = "json_file_payload"
    advisory_only = IO_UTILS_ADVISORY_ONLY
    authority_metadata = _authority_metadata(
        operation="write_json_file",
        target_path=target,
        extra={"indent": indent},
    )

    if isinstance(payload, dict):
        governed_payload: Dict[str, Any] = dict(payload)
    else:
        governed_payload = {
            "artifact_type": "json_payload",
            "payload": payload,
        }

    governed_payload.setdefault("classification", _classification_block())
    governed_payload.setdefault("authority_metadata", authority_metadata)
    governed_payload.setdefault("sealed", True)

    governed_write_raw_json(
        path=target,
        payload=governed_payload,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        advisory_only=advisory_only,
    )

    return target