from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .continuity_mutation_receipt_builder import (
    build_failure_receipt,
    build_mutation_receipt,
)
from .continuity_mutation_registry import (
    CURRENT_MUTATION_POLICY_VERSION,
    is_allowed_scope,
    is_allowed_upstream_intake_policy_version,
    is_registered_target,
)
from .continuity_store import ContinuityStore


store = ContinuityStore()


REQUIRED_RECEIPT_KEYS = {
    "receipt_type",
    "intake_id",
    "target_core",
    "continuity_scope",
    "admission_basis",
    "watcher_receipt_ref",
    "output_disposition_ref",
    "runtime_ref",
    "policy_version",
    "timestamp",
}

LINEAGE_KEYS = {
    "watcher_receipt_ref",
    "output_disposition_ref",
    "runtime_ref",
}


def reset_store() -> None:
    store.reset()


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _validate_receipt_structure(receipt: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(receipt, dict):
        return False, "invalid_input", "receipt must be a dictionary"

    if receipt.get("receipt_type") != "continuity_intake_receipt":
        return False, "invalid_input", "invalid receipt type"

    missing = [key for key in sorted(REQUIRED_RECEIPT_KEYS) if key not in receipt]
    if missing:
        return False, "structural_invalid", f"missing required receipt keys: {', '.join(missing)}"

    bad_keys = [key for key in sorted(REQUIRED_RECEIPT_KEYS - LINEAGE_KEYS) if not _is_non_empty_string(receipt.get(key))]
    if bad_keys:
        return False, "structural_invalid", f"receipt keys must be non-empty strings: {', '.join(bad_keys)}"

    return True, None, "valid"


def _validate_lineage(receipt: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    bad_refs = [key for key in sorted(LINEAGE_KEYS) if not _is_non_empty_string(receipt.get(key))]
    if bad_refs:
        return False, "lineage_broken", f"required lineage refs missing or empty: {', '.join(bad_refs)}"
    return True, None, "valid"


def _validate_registry(receipt: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    target = receipt["target_core"]
    scope = receipt["continuity_scope"]
    upstream_policy_version = receipt["policy_version"]

    if not is_registered_target(target):
        return False, "scope_unlawful", "unknown target core"

    if not is_allowed_scope(target, scope):
        return False, "scope_unlawful", "invalid continuity scope for target"

    if not is_allowed_upstream_intake_policy_version(target, upstream_policy_version):
        return False, "policy_version_invalid", "upstream intake policy version is not allowed"

    return True, None, "valid"


def _make_continuity_key(receipt: Dict[str, Any]) -> str:
    return f"{receipt['target_core']}::{receipt['continuity_scope']}::{receipt['intake_id']}"


def process_continuity_mutation(receipt: dict):
    upstream_policy_version = receipt.get("policy_version") if isinstance(receipt, dict) else None

    structure_ok, structure_code, structure_reason = _validate_receipt_structure(receipt)
    if not structure_ok:
        return build_failure_receipt(
            target_core=receipt.get("target_core") if isinstance(receipt, dict) else None,
            code=structure_code or "invalid_input",
            reason=structure_reason,
            upstream_policy_version=upstream_policy_version,
            mutation_policy_version=CURRENT_MUTATION_POLICY_VERSION,
        )

    lineage_ok, lineage_code, lineage_reason = _validate_lineage(receipt)
    if not lineage_ok:
        return build_failure_receipt(
            target_core=receipt["target_core"],
            code=lineage_code or "lineage_broken",
            reason=lineage_reason,
            upstream_policy_version=receipt["policy_version"],
            mutation_policy_version=CURRENT_MUTATION_POLICY_VERSION,
        )

    registry_ok, registry_code, registry_reason = _validate_registry(receipt)
    if not registry_ok:
        return build_failure_receipt(
            target_core=receipt["target_core"],
            code=registry_code or "scope_unlawful",
            reason=registry_reason,
            upstream_policy_version=receipt["policy_version"],
            mutation_policy_version=CURRENT_MUTATION_POLICY_VERSION,
        )

    continuity_key = _make_continuity_key(receipt)

    if store.exists(continuity_key):
        return build_mutation_receipt(
            target_core=receipt["target_core"],
            mutation_type="no_op",
            intake_id=receipt["intake_id"],
            upstream_policy_version=receipt["policy_version"],
            mutation_policy_version=CURRENT_MUTATION_POLICY_VERSION,
        )

    record = {
        "continuity_key": continuity_key,
        "intake_id": receipt["intake_id"],
        "target_core": receipt["target_core"],
        "continuity_scope": receipt["continuity_scope"],
        "admission_basis": receipt["admission_basis"],
        "watcher_receipt_ref": receipt["watcher_receipt_ref"],
        "output_disposition_ref": receipt["output_disposition_ref"],
        "runtime_ref": receipt["runtime_ref"],
        "upstream_policy_version": receipt["policy_version"],
        "mutation_policy_version": CURRENT_MUTATION_POLICY_VERSION,
        "source_timestamp": receipt["timestamp"],
    }

    store.write(continuity_key, record)

    return build_mutation_receipt(
        target_core=receipt["target_core"],
        mutation_type="created",
        intake_id=receipt["intake_id"],
        upstream_policy_version=receipt["policy_version"],
        mutation_policy_version=CURRENT_MUTATION_POLICY_VERSION,
    )