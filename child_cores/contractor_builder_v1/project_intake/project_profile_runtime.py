from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import contractor_projects_root
from AI_GO.core.state_runtime.state_paths import contractor_projects_root


PROJECTS_ROOT = contractor_projects_root()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_project_profile",
        "mutation_class": "root_project_state_creation",
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
        "layer": "project_intake.project_profile_runtime",
        "project_id": _safe_str(project_id),
    }


def get_project_root(project_id: str) -> Path:
    return PROJECTS_ROOT / _safe_str(project_id)


def get_project_profile_path(project_id: str) -> Path:
    return get_project_root(project_id) / "project_profile.json"


def build_project_profile(
    *,
    project_id: str,
    project_name: str,
    project_type: str,
    project_description: str = "",
    client_name: str = "",
    client_email: str = "",
    pm_name: str = "",
    pm_email: str = "",
    site_address: str = "",
    city: str = "",
    county: str = "",
    state: str = "",
    authority_name: str = "",
    portfolio_id: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    return {
        "artifact_type": "contractor_project_profile",
        "artifact_version": "northstar_project_profile_v1",
        "created_at": _utc_now_iso(),
        "project_id": clean_project_id,
        "project_name": _safe_str(project_name),
        "project_type": _safe_str(project_type),
        "project_description": _safe_str(project_description),
        "status": "active",
        "portfolio_id": _safe_str(portfolio_id),
        "client": {
            "name": _safe_str(client_name),
            "email": _safe_str(client_email),
        },
        "pm": {
            "name": _safe_str(pm_name),
            "email": _safe_str(pm_email),
        },
        "site": {
            "address": _safe_str(site_address),
            "city": _safe_str(city),
            "county": _safe_str(county),
            "state": _safe_str(state),
        },
        "jurisdiction": {
            "authority_name": _safe_str(authority_name),
            "city": _safe_str(city),
            "county": _safe_str(county),
            "state": _safe_str(state),
        },
        "notes": _safe_str(notes),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(clean_project_id, "build_project_profile"),
        "sealed": True,
    }


def create_project_profile_record(
    *,
    project_id: str,
    project_name: str,
    project_type: str,
    project_description: str = "",
    client_name: str = "",
    client_email: str = "",
    pm_name: str = "",
    pm_email: str = "",
    site_address: str = "",
    city: str = "",
    county: str = "",
    state: str = "",
    authority_name: str = "",
    portfolio_id: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """
    Backward-compatible public contract expected by project_profile.py and
    project_intake_runner.py.
    """
    return build_project_profile(
        project_id=project_id,
        project_name=project_name,
        project_type=project_type,
        project_description=project_description,
        client_name=client_name,
        client_email=client_email,
        pm_name=pm_name,
        pm_email=pm_email,
        site_address=site_address,
        city=city,
        county=county,
        state=state,
        authority_name=authority_name,
        portfolio_id=portfolio_id,
        notes=notes,
    )


def write_project_profile(profile: Dict[str, Any]) -> str:
    if not isinstance(profile, dict):
        raise ValueError("profile must be a dict")

    project_id = _safe_str(profile.get("project_id"))
    if not project_id:
        raise ValueError("project_id is required")

    payload = dict(profile)
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(project_id, "write_project_profile")
    payload["sealed"] = True

    path = get_project_profile_path(project_id)

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="root_project_state_creation",
        persistence_type="contractor_project_profile",
        authority_metadata=payload["authority_metadata"],
    )

    return str(path)


def write_project_profile_record(profile: Dict[str, Any]) -> str:
    """
    Backward-compatible alias for callers expecting *_record naming.
    """
    return write_project_profile(profile)


def load_project_profile(project_id: str) -> Dict[str, Any]:
    path = get_project_profile_path(project_id)
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return payload if isinstance(payload, dict) else {}
