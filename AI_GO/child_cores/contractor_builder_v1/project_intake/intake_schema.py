from __future__ import annotations

from typing import Any, Dict, List


REQUIRED_FIELDS = [
    "project_name",
    "project_type",
    "client_name",
    "pm_name",
    "jurisdiction",
    "baseline_refs",
]


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


# ============================================================
# ✅ CANONICAL INTAKE BUILDER (THIS WAS MISSING)
# ============================================================

def build_project_intake_payload(
    *,
    project_name: str,
    project_type: str,
    client_name: str,
    pm_name: str,
    jurisdiction: Dict[str, Any],
    baseline_refs: Dict[str, Any],
    project_description: str = "",
    client_contact: str = "",
    pm_contact: str = "",
    site_address: str = "",
    portfolio_id: str = "",
    oracle_snapshot_id: str = "",
    exposure_profile_id: str = "",
    notes: str = "",
) -> Dict[str, Any]:

    return {
        "project_name": _clean(project_name),
        "project_type": _clean(project_type),
        "client_name": _clean(client_name),
        "pm_name": _clean(pm_name),
        "jurisdiction": _dict(jurisdiction),
        "baseline_refs": _dict(baseline_refs),

        # optional fields
        "project_description": _clean(project_description),
        "client_contact": _clean(client_contact),
        "pm_contact": _clean(pm_contact),
        "site_address": _clean(site_address),
        "portfolio_id": _clean(portfolio_id),
        "oracle_snapshot_id": _clean(oracle_snapshot_id),
        "exposure_profile_id": _clean(exposure_profile_id),
        "notes": _clean(notes),
    }


# ============================================================
# ✅ VALIDATION
# ============================================================

def validate_project_intake_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload_must_be_dict"]

    for field in REQUIRED_FIELDS:
        value = payload.get(field)

        if field in ("jurisdiction", "baseline_refs"):
            if not isinstance(value, dict) or not value:
                errors.append(f"{field}_must_be_non_empty_dict")
        else:
            if not _clean(value):
                errors.append(f"{field}_required")

    return sorted(set(errors))