"""
RESEARCH_CORE.intake.intake

Lawful intake entry surface for raw research signal.
This module normalizes incoming payloads into a governed intake shape
before downstream screening occurs.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.shared.timestamps import utc_now_iso
from core.shared.ids import build_prefixed_id
from core.shared.schemas import require_keys, require_non_empty_string
from core.shared.utils import ensure_list, compact_strings


INTAKE_REQUIRED_KEYS = ["title", "summary"]


def normalize_intake_payload(
    payload: Dict[str, Any],
    *,
    issuing_authority: str = "RESEARCH_CORE",
    default_scope: str = "core",
) -> Dict[str, Any]:
    """
    Normalize a raw research payload into a governed intake record.
    """
    require_keys(payload, INTAKE_REQUIRED_KEYS)

    title = require_non_empty_string(payload["title"], "title")
    summary = require_non_empty_string(payload["summary"], "summary")
    scope = str(payload.get("scope", default_scope)).strip() or default_scope

    source_refs = ensure_list(payload.get("source_refs"))
    tags = compact_strings(ensure_list(payload.get("tags")))

    intake_record = {
        "intake_id": build_prefixed_id("WR-RESEARCH-INTAKE"),
        "title": title,
        "summary": summary,
        "source_refs": source_refs,
        "scope": scope,
        "tags": tags,
        "notes": payload.get("notes"),
        "ingested_at": utc_now_iso(),
        "issuing_authority": issuing_authority,
        "status": "intake_normalized",
    }

    return intake_record


def build_intake_batch(
    payloads: List[Dict[str, Any]],
    *,
    issuing_authority: str = "RESEARCH_CORE",
    default_scope: str = "core",
) -> List[Dict[str, Any]]:
    """
    Normalize a batch of intake payloads.
    """
    return [
        normalize_intake_payload(
            payload,
            issuing_authority=issuing_authority,
            default_scope=default_scope,
        )
        for payload in payloads
    ]