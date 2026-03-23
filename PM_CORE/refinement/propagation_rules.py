from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_pm_active_dir() -> Path:
    return get_project_root() / "PM_CORE" / "state" / "active"


def _slugify(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = []

    for ch in text:
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in {" ", "-", "_"}:
            cleaned.append("_")

    slug = "".join(cleaned).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")

    return slug or "pm_interpretation"


def build_strategic_interpretation(
    *,
    research_packet: Dict[str, Any],
    screening_result: Dict[str, Any],
    trust_result: Dict[str, Any],
) -> Dict[str, Any]:
    packet_id = research_packet.get("packet_id")
    title = research_packet.get("title")
    summary = research_packet.get("summary")
    scope = research_packet.get("scope")
    tags = research_packet.get("tags", [])
    source_refs = research_packet.get("source_refs", [])

    trust_class = trust_result.get("trust_class")
    screening_status = screening_result.get("screening_status")

    priority = _derive_priority(
        trust_class=trust_class,
        source_ref_count=len(source_refs),
    )

    recommended_action = _derive_recommended_action(
        trust_class=trust_class,
        screening_status=screening_status,
    )

    interpretation = {
        "interpretation_type": "pm_strategic_interpretation",
        "recorded_at": _utc_now_iso(),
        "source_packet_id": packet_id,
        "title": title,
        "summary": summary,
        "scope": scope,
        "tags": tags,
        "source_ref_count": len(source_refs),
        "screening_status": screening_status,
        "trust_class": trust_class,
        "priority": priority,
        "recommended_action": recommended_action,
        "planning_scope": _derive_planning_scope(scope=scope, tags=tags),
        "constraints": _derive_constraints(
            trust_class=trust_class,
            source_ref_count=len(source_refs),
        ),
        "signals": _derive_signals(
            trust_class=trust_class,
            screening_status=screening_status,
            tags=tags,
        ),
    }

    return interpretation


def persist_strategic_interpretation(
    interpretation: Dict[str, Any],
) -> Dict[str, Any]:
    active_dir = get_pm_active_dir()
    active_dir.mkdir(parents=True, exist_ok=True)

    packet_id = interpretation.get("source_packet_id")
    title = interpretation.get("title") or interpretation.get("summary") or "pm_interpretation"
    path = active_dir / f"{packet_id}__{_slugify(title)}__pm_interpretation.json"

    with path.open("w", encoding="utf-8") as handle:
        json.dump(interpretation, handle, indent=2, ensure_ascii=False)

    return {
        "status": "recorded",
        "interpretation_path": str(path),
        "interpretation": interpretation,
    }


def _derive_priority(*, trust_class: str | None, source_ref_count: int) -> str:
    if trust_class == "verified" and source_ref_count > 0:
        return "high"
    if trust_class in {"verified", "screened"}:
        return "medium"
    return "low"


def _derive_recommended_action(*, trust_class: str | None, screening_status: str | None) -> str:
    if screening_status != "passed":
        return "defer"

    if trust_class == "verified":
        return "prepare_inheritance"

    if trust_class == "screened":
        return "retain_for_pm_review"

    return "defer"


def _derive_planning_scope(*, scope: Any, tags: List[str]) -> str:
    if scope == "core":
        return "core_strategy"

    if any(tag.endswith("_core") for tag in tags):
        return "domain_strategy"

    return "local_strategy"


def _derive_constraints(*, trust_class: str | None, source_ref_count: int) -> List[str]:
    constraints = [
        "PM interpretation may not rewrite research packet truth.",
        "Child-core propagation requires governed inheritance packetization.",
    ]

    if trust_class != "verified":
        constraints.append("Non-verified trust class may not auto-propagate to child cores.")

    if source_ref_count == 0:
        constraints.append("Interpretation should be treated as low-evidence until source references increase.")

    return constraints


def _derive_signals(
    *,
    trust_class: str | None,
    screening_status: str | None,
    tags: List[str],
) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = [
        {
            "signal_type": "screening_status",
            "value": screening_status,
        },
        {
            "signal_type": "trust_class",
            "value": trust_class,
        },
    ]

    if tags:
        signals.append(
            {
                "signal_type": "tag_set",
                "value": tags,
            }
        )

    return signals