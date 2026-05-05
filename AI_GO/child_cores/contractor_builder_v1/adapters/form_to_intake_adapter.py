from __future__ import annotations

from datetime import UTC, datetime
from secrets import token_hex
from typing import Any, Dict

from ..project_intake.intake_schema import build_project_intake_payload


def _utc_timestamp_compact() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _slugify(value: str) -> str:
    cleaned: list[str] = []
    for char in (value or "").strip().lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "-", "_", "/", ".", ","}:
            cleaned.append("-")
    slug = "".join(cleaned)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "unknown"


def _build_default_ref(prefix: str, scope: str) -> str:
    return f"{prefix}-{_slugify(scope)}-{_utc_timestamp_compact()}-{token_hex(2)}"


def build_jurisdiction_from_form(
    *,
    city: str,
    county: str,
    state: str,
    authority_name: str = "",
) -> Dict[str, Any]:
    state_clean = (state or "").strip().upper()
    city_clean = (city or "").strip()
    county_clean = (county or "").strip()

    jurisdiction_scope = "-".join(
        part for part in [city_clean, county_clean, state_clean] if part
    ) or "unknown"

    return {
        "jurisdiction_id": _slugify(jurisdiction_scope),
        "authority_name": authority_name.strip(),
        "city": city_clean,
        "county": county_clean,
        "state": state_clean,
    }


def build_default_baseline_refs(
    *,
    project_name: str,
    state: str,
) -> Dict[str, Any]:
    scope = f"{project_name}-{state}"
    return {
        "schedule_baseline_id": _build_default_ref("schedule-baseline", scope),
        "budget_baseline_id": _build_default_ref("budget-baseline", scope),
        "compliance_snapshot_id": _build_default_ref("compliance-snapshot", scope),
    }


def build_form_echo(form_input: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "project_name": str(form_input.get("project_name", "")).strip(),
        "project_type": str(form_input.get("project_type", "")).strip(),
        "project_description": str(form_input.get("project_description", "")).strip(),
        "client_name": str(form_input.get("client_name", "")).strip(),
        "client_email": str(form_input.get("client_email", "")).strip(),
        "pm_name": str(form_input.get("pm_name", "")).strip(),
        "pm_email": str(form_input.get("pm_email", "")).strip(),
        "site_address": str(form_input.get("site_address", "")).strip(),
        "city": str(form_input.get("city", "")).strip(),
        "county": str(form_input.get("county", "")).strip(),
        "state": str(form_input.get("state", "")).strip().upper(),
        "authority_name": str(form_input.get("authority_name", "")).strip(),
        "portfolio_id": str(form_input.get("portfolio_id", "")).strip(),
        "notes": str(form_input.get("notes", "")).strip(),
    }


def build_intake_payload_from_form(form_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a simple form payload into the canonical intake payload expected by the
    project_intake layer.
    """
    if not isinstance(form_input, dict) or not form_input:
        raise ValueError("form_input must be a non-empty mapping")

    form_echo = build_form_echo(form_input)

    jurisdiction = build_jurisdiction_from_form(
        city=form_echo["city"],
        county=form_echo["county"],
        state=form_echo["state"],
        authority_name=form_echo["authority_name"],
    )

    baseline_refs = build_default_baseline_refs(
        project_name=form_echo["project_name"],
        state=form_echo["state"],
    )

    return build_project_intake_payload(
        project_name=form_echo["project_name"],
        project_type=form_echo["project_type"],
        client_name=form_echo["client_name"],
        pm_name=form_echo["pm_name"],
        jurisdiction=jurisdiction,
        baseline_refs=baseline_refs,
        project_description=form_echo["project_description"],
        client_contact=form_echo["client_email"],
        pm_contact=form_echo["pm_email"],
        site_address=form_echo["site_address"],
        portfolio_id=form_echo["portfolio_id"],
        notes=form_echo["notes"],
    )