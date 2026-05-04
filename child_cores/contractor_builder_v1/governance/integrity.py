"""
Integrity helpers for contractor_builder_v1.

This module provides canonical hashing and integrity block construction for
append-only records, sealed packets, and receipt-linked artifacts.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Optional


def canonical_json_dumps(payload: Any) -> str:
    """
    Serialize payload into canonical JSON for deterministic hashing.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def compute_hash_for_text(value: str) -> str:
    """
    Compute a SHA-256 hash for plain text.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_hash_for_mapping(mapping: Mapping[str, Any]) -> str:
    """
    Compute a SHA-256 hash for a JSON-serializable mapping.
    """
    return compute_hash_for_text(canonical_json_dumps(dict(mapping)))


def with_integrity_block(
    record: Mapping[str, Any],
    *,
    receipt_ids: Optional[Iterable[str]] = None,
    supersedes_id: Optional[str] = None,
    hash_field_name: str = "entry_hash",
) -> Dict[str, Any]:
    """
    Return a copy of a record with an integrity block attached.

    The integrity hash is computed over the record without any pre-existing integrity
    block to avoid recursive hashing.
    """
    base = dict(record)
    base.pop("integrity", None)

    integrity_hash = compute_hash_for_mapping(base)

    integrity_block: Dict[str, Any] = {
        hash_field_name: integrity_hash,
        "linked_receipts": list(receipt_ids or []),
    }
    if supersedes_id is not None:
        integrity_block["supersedes_id"] = supersedes_id

    enriched = dict(base)
    enriched["integrity"] = integrity_block
    return enriched