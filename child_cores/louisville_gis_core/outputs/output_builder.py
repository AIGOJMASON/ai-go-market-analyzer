from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_outputs_dir() -> Path:
    return get_project_root() / "child_cores" / "louisville_gis_core" / "outputs"


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

    return slug or "child_core_output"


def build_louisville_gis_output(
    *,
    inheritance_packet: Dict[str, Any],
    execution_record: Dict[str, Any],
) -> Dict[str, Any]:
    source_summary = inheritance_packet.get("source_summary")
    source_title = inheritance_packet.get("source_title")
    source_packet_id = inheritance_packet.get("source_packet_id")

    return {
        "output_type": "child_core_execution_output",
        "core_id": "louisville_gis_core",
        "recorded_at": _utc_now_iso(),
        "source_packet_id": source_packet_id,
        "source_title": source_title,
        "source_summary": source_summary,
        "execution_id": execution_record.get("execution_id"),
        "status": "prepared",
        "recommended_next_step": "review_louisville_gis_opportunity",
        "domain_focus": "louisville_gis",
        "notes": [
            "Bounded ingress activation completed.",
            "This output does not authorize autonomous domain expansion.",
            "Further GIS-specific execution must be versioned separately.",
        ],
    }


def persist_louisville_gis_output(
    output_payload: Dict[str, Any],
) -> Dict[str, Any]:
    outputs_dir = get_outputs_dir()
    outputs_dir.mkdir(parents=True, exist_ok=True)

    source_packet_id = output_payload.get("source_packet_id") or "unknown_packet"
    source_title = output_payload.get("source_title") or output_payload.get("source_summary") or "louisville_gis_output"
    path = outputs_dir / f"{source_packet_id}__{_slugify(source_title)}__output.json"

    with path.open("w", encoding="utf-8") as handle:
        json.dump(output_payload, handle, indent=2, ensure_ascii=False)

    return {
        "status": "recorded",
        "output_path": str(path),
        "output": output_payload,
    }