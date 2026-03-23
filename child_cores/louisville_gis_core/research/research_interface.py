from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_core_root() -> Path:
    return get_project_root() / "child_cores" / "louisville_gis_core"


def load_domain_registry() -> Dict[str, Any]:
    path = get_core_root() / "DOMAIN_REGISTRY.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Louisville GIS domain registry must decode to a dict")

    return payload


def validate_domain_research_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    registry = load_domain_registry()
    theme = payload.get("theme")
    summary = payload.get("summary")
    source_refs = payload.get("source_refs", [])

    reasons: List[str] = []

    if not isinstance(theme, str) or not theme.strip():
        reasons.append("missing_theme")

    if not isinstance(summary, str) or not summary.strip():
        reasons.append("missing_summary")

    if not isinstance(source_refs, list) or not all(isinstance(item, str) for item in source_refs):
        reasons.append("invalid_source_refs")

    allowed_themes = registry.get("research_themes", [])
    if isinstance(theme, str) and theme.strip() and theme not in allowed_themes:
        reasons.append(f"theme_not_registered:{theme}")

    return {
        "status": "accepted" if not reasons else "rejected",
        "domain_focus": registry.get("domain_focus"),
        "theme": theme,
        "summary": summary,
        "source_refs": source_refs,
        "reasons": reasons,
    }