# AI_GO/core/governance/governed_persistence.py

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


GOVERNED_PERSISTENCE_VERSION = "northstar_6a_governed_persistence_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _classification(
    *,
    mutation_class: str,
    persistence_type: str,
    advisory_only: bool,
) -> Dict[str, Any]:
    return {
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "advisory_only": bool(advisory_only),
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "governed_persistence": True,
    }


def build_authority_metadata(
    *,
    authority_id: str = "core_governance_governed_persistence",
    operation: str = "write_json",
    actor: str = "system",
    source: str = "",
    child_core_id: str = "",
    project_id: str = "",
    request_id: str = "",
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = {
        "authority_id": _clean(authority_id) or "core_governance_governed_persistence",
        "operation": _clean(operation) or "write_json",
        "actor": _clean(actor) or "system",
        "source": _clean(source),
        "child_core_id": _clean(child_core_id),
        "project_id": _clean(project_id),
        "request_id": _clean(request_id),
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_recommendations": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "append_only_memory": False,
        "governance_stage": "northstar_6a",
    }

    metadata.update(_as_dict(extra))
    return metadata


def _normalize_authority_metadata(
    *,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    operation: str = "write_json",
    actor: str = "system",
    source: str = "",
    child_core_id: str = "",
    project_id: str = "",
    request_id: str = "",
) -> Dict[str, Any]:
    supplied = _as_dict(authority_metadata) or _as_dict(authority)

    if supplied:
        normalized = build_authority_metadata(
            authority_id=str(supplied.get("authority_id") or "core_governance_governed_persistence"),
            operation=str(supplied.get("operation") or operation),
            actor=str(supplied.get("actor") or actor),
            source=str(supplied.get("source") or source),
            child_core_id=str(supplied.get("child_core_id") or child_core_id),
            project_id=str(supplied.get("project_id") or project_id),
            request_id=str(supplied.get("request_id") or request_id),
            extra=supplied,
        )
        return normalized

    return build_authority_metadata(
        operation=operation,
        actor=actor,
        source=source,
        child_core_id=child_core_id,
        project_id=project_id,
        request_id=request_id,
    )


def build_governed_envelope(
    *,
    payload: Any,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
    artifact_type: str = "governed_persistence_envelope",
    artifact_version: str = GOVERNED_PERSISTENCE_VERSION,
) -> Dict[str, Any]:
    mutation_class = _clean(mutation_class)
    persistence_type = _clean(persistence_type)
    authority = _normalize_authority_metadata(
        authority_metadata=authority_metadata,
        operation="build_governed_envelope",
    )

    if not mutation_class:
        raise ValueError("mutation_class is required")
    if not persistence_type:
        raise ValueError("persistence_type is required")

    return {
        "artifact_type": _clean(artifact_type) or "governed_persistence_envelope",
        "artifact_version": _clean(artifact_version) or GOVERNED_PERSISTENCE_VERSION,
        "persisted_at": _utc_now_iso(),
        "classification": _classification(
            mutation_class=mutation_class,
            persistence_type=persistence_type,
            advisory_only=advisory_only,
        ),
        "authority_metadata": authority,
        "payload": payload,
        "sealed": True,
    }


def _atomic_write_bytes(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_bytes(data)
    os.replace(tmp_path, path)
    return path


def governed_write_json(
    *,
    path: str | Path | None = None,
    output_path: str | Path | None = None,
    payload: Any = None,
    data: Any = None,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
    artifact_type: str = "governed_persistence_envelope",
    artifact_version: str = GOVERNED_PERSISTENCE_VERSION,
    sort_keys: bool = True,
) -> Dict[str, Any]:
    target_value = path or output_path
    if target_value is None:
        raise ValueError("path is required")

    target = Path(target_value)
    body = payload if payload is not None else data

    normalized_authority = _normalize_authority_metadata(
        authority_metadata=authority_metadata,
        authority=authority,
        operation="write_json",
    )

    envelope = build_governed_envelope(
        payload=body,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=normalized_authority,
        advisory_only=advisory_only,
        artifact_type=artifact_type,
        artifact_version=artifact_version,
    )

    serialized = json.dumps(
        envelope,
        indent=2,
        sort_keys=sort_keys,
        ensure_ascii=False,
        default=str,
    )

    # NORTHSTAR 6A WRITE BOUNDARY:
    # mutation_class, persistence_type, authority_metadata, advisory_only
    _atomic_write_bytes(target, (serialized + "\n").encode("utf-8"))

    return {
        "status": "persisted",
        "path": str(target),
        "output_path": str(target),
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "authority_metadata": normalized_authority,
        "advisory_only": bool(advisory_only),
        "artifact_type": artifact_type,
        "artifact_version": artifact_version,
    }


def governed_write_raw_json(
    *,
    path: str | Path | None = None,
    output_path: str | Path | None = None,
    payload: Any = None,
    data: Any = None,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
    sort_keys: bool = True,
) -> Dict[str, Any]:
    target_value = path or output_path
    if target_value is None:
        raise ValueError("path is required")

    target = Path(target_value)
    body = payload if payload is not None else data

    if not _clean(mutation_class):
        raise ValueError("mutation_class is required")
    if not _clean(persistence_type):
        raise ValueError("persistence_type is required")

    normalized_authority = _normalize_authority_metadata(
        authority_metadata=authority_metadata,
        authority=authority,
        operation="write_raw_json",
    )

    if isinstance(body, dict):
        raw_payload = dict(body)
        raw_payload.setdefault(
            "classification",
            _classification(
                mutation_class=mutation_class,
                persistence_type=persistence_type,
                advisory_only=advisory_only,
            ),
        )
        raw_payload.setdefault("authority_metadata", normalized_authority)
        raw_payload.setdefault("sealed", True)
    else:
        raw_payload = body

    serialized = json.dumps(
        raw_payload,
        indent=2,
        sort_keys=sort_keys,
        ensure_ascii=False,
        default=str,
    )

    # NORTHSTAR 6A RAW WRITE BOUNDARY:
    # mutation_class, persistence_type, authority_metadata, advisory_only
    _atomic_write_bytes(target, (serialized + "\n").encode("utf-8"))

    return {
        "status": "persisted",
        "path": str(target),
        "output_path": str(target),
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "authority_metadata": normalized_authority,
        "advisory_only": bool(advisory_only),
        "raw_payload": True,
    }


def governed_append_jsonl(
    *,
    path: str | Path | None = None,
    output_path: str | Path | None = None,
    record: Mapping[str, Any] | None = None,
    payload: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
) -> Dict[str, Any]:
    target_value = path or output_path
    if target_value is None:
        raise ValueError("path is required")

    target = Path(target_value)
    record_body = record if record is not None else payload if payload is not None else data
    if not isinstance(record_body, Mapping):
        raise ValueError("record must be a mapping")

    normalized_authority = _normalize_authority_metadata(
        authority_metadata=authority_metadata,
        authority=authority,
        operation="append_jsonl",
    )

    envelope = build_governed_envelope(
        payload=dict(record_body),
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=normalized_authority,
        advisory_only=advisory_only,
        artifact_type="governed_jsonl_record",
    )

    existing = ""
    if target.exists():
        existing = target.read_text(encoding="utf-8", errors="ignore")

    line = json.dumps(envelope, sort_keys=True, ensure_ascii=False, default=str)
    combined = existing
    if combined and not combined.endswith("\n"):
        combined += "\n"
    combined += line + "\n"

    # NORTHSTAR 6A JSONL WRITE BOUNDARY:
    # mutation_class, persistence_type, authority_metadata, advisory_only
    _atomic_write_bytes(target, combined.encode("utf-8"))

    return {
        "status": "appended",
        "path": str(target),
        "output_path": str(target),
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "authority_metadata": normalized_authority,
        "advisory_only": bool(advisory_only),
    }


def load_json(path: str | Path, default: Any = None, *, unwrap_envelope: bool = True) -> Any:
    target = Path(path)
    if not target.exists():
        return default

    try:
        parsed = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return default

    if (
        unwrap_envelope
        and isinstance(parsed, dict)
        and parsed.get("artifact_type") == "governed_persistence_envelope"
    ):
        return parsed.get("payload", default)

    return parsed


def load_jsonl(path: str | Path, *, unwrap_envelope: bool = True) -> List[Any]:
    target = Path(path)
    if not target.exists():
        return []

    rows: List[Any] = []
    for line in target.read_text(encoding="utf-8", errors="ignore").splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        try:
            parsed = json.loads(cleaned)
        except Exception:
            continue

        if (
            unwrap_envelope
            and isinstance(parsed, dict)
            and parsed.get("artifact_type") == "governed_jsonl_record"
        ):
            rows.append(parsed.get("payload"))
        else:
            rows.append(parsed)

    return rows


def write_json(
    path: str | Path,
    payload: Any,
    *,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
) -> Dict[str, Any]:
    return governed_write_json(
        path=path,
        payload=payload,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        authority=authority,
        advisory_only=advisory_only,
    )


def append_jsonl(
    path: str | Path,
    record: Mapping[str, Any],
    *,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    advisory_only: bool = False,
) -> Dict[str, Any]:
    return governed_append_jsonl(
        path=path,
        record=record,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        authority=authority,
        advisory_only=advisory_only,
    )