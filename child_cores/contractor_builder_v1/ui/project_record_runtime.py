from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import contractor_project_root


PROJECT_RECORD_RUNTIME_VERSION = "northstar_project_record_runtime_v1"
MUTATION_CLASS = "contractor_project_record_persistence"
PERSISTENCE_TYPE = "contractor_project_record"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _project_root(project_id: str) -> Path:
    return contractor_project_root(_safe_str(project_id))


def get_project_record_path(project_id: str) -> Path:
    return _project_root(project_id) / "project_record.json"


def get_project_profile_path(project_id: str) -> Path:
    return _project_root(project_id) / "project_profile.json"


def get_baseline_lock_path(project_id: str) -> Path:
    return _project_root(project_id) / "project_intake" / "baseline_lock.json"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "project_truth_mutation_allowed": True,
        "advisory_only": False,
    }


def _authority_metadata(project_id: str, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "ui.project_record_runtime",
        "project_id": _safe_str(project_id),
    }


def _unwrap_payload(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    if (
        payload.get("artifact_type") == "governed_persistence_envelope"
        and isinstance(payload.get("payload"), dict)
    ):
        return dict(payload["payload"])
    return dict(payload)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return _unwrap_payload(json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return {}


def build_project_record(
    *,
    project_id: str,
    project_profile: Dict[str, Any] | None = None,
    baseline_lock: Dict[str, Any] | None = None,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    profile = _safe_dict(project_profile)
    baseline = _safe_dict(baseline_lock)

    return {
        "artifact_type": "contractor_project_record",
        "artifact_version": PROJECT_RECORD_RUNTIME_VERSION,
        "project_id": clean_project_id,
        "project_profile": profile,
        "baseline_lock": baseline,
        "extra": _safe_dict(extra),
        "generated_at": _utc_now_iso(),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(clean_project_id, "build_project_record"),
        "sealed": True,
    }


def load_project_record(project_id: str) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    record = _read_json(get_project_record_path(clean_project_id))
    if record:
        record.setdefault("classification", _classification_block())
        record.setdefault(
            "authority_metadata",
            _authority_metadata(clean_project_id, "load_project_record"),
        )
        record.setdefault("sealed", True)
        return record

    profile = _read_json(get_project_profile_path(clean_project_id))
    baseline = _read_json(get_baseline_lock_path(clean_project_id))

    if not profile and not baseline:
        return {}

    return build_project_record(
        project_id=clean_project_id,
        project_profile=profile,
        baseline_lock=baseline,
    )


def write_project_record(record: Dict[str, Any]) -> Path:
    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    project_id = _safe_str(record.get("project_id"))
    if not project_id:
        raise ValueError("project_id is required")

    payload = dict(record)
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(project_id, "write_project_record")
    payload["sealed"] = True

    path = get_project_record_path(project_id)

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class=MUTATION_CLASS,
        persistence_type=PERSISTENCE_TYPE,
        authority_metadata=payload["authority_metadata"],
    )

    return path