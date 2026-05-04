from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


MEMORY_AUTHORITY_GUARD_VERSION = "v5F.1"

FORBIDDEN_TRUE_CLAIMS = {
    "memory_is_truth",
    "can_override_state_authority",
    "can_override_canon",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_execute",
    "can_mutate_runtime",
    "can_mutate_state",
    "can_mutate_operational_state",
    "can_mutate_child_core_state",
    "can_bypass_governance",
    "can_bypass_watcher",
    "can_bypass_execution_gate",
    "runtime_authority",
    "execution_authority",
    "state_authority",
    "canon_authority",
    "watcher_authority",
}

REQUIRED_FALSE_CLAIMS = {
    "memory_is_truth": False,
    "can_override_state_authority": False,
    "can_override_canon": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_state": False,
    "can_mutate_operational_state": False,
    "can_mutate_child_core_state": False,
}

REQUIRED_TRUE_CLAIMS = {
    "memory_is_candidate_signal": True,
    "advisory_only": True,
    "read_only_to_authority_chain": True,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _authority_from_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    authority = dict(_safe_dict(artifact.get("authority")))

    for key, value in REQUIRED_FALSE_CLAIMS.items():
        authority.setdefault(key, value)

    for key, value in REQUIRED_TRUE_CLAIMS.items():
        authority.setdefault(key, value)

    authority.setdefault("guard_version", MEMORY_AUTHORITY_GUARD_VERSION)
    authority.setdefault("memory_role", "candidate_signal_only")
    authority.setdefault("truth_source", False)

    return authority


def build_memory_authority_policy() -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_authority_policy",
        "artifact_version": MEMORY_AUTHORITY_GUARD_VERSION,
        "generated_at": _utc_now_iso(),
        "law": "Memory is candidate signal only. Memory is never truth authority.",
        "required_true_claims": dict(REQUIRED_TRUE_CLAIMS),
        "required_false_claims": dict(REQUIRED_FALSE_CLAIMS),
        "forbidden_true_claims": sorted(FORBIDDEN_TRUE_CLAIMS),
        "may_feed": [
            "pattern_context",
            "system_brain_advisory_surface",
            "operator_visibility",
        ],
        "may_not_feed": [
            "state_authority_override",
            "canon_override",
            "watcher_override",
            "execution_gate_override",
            "runtime_mutation",
            "direct_execution",
        ],
        "sealed": True,
    }


def evaluate_memory_authority(artifact: Dict[str, Any]) -> Dict[str, Any]:
    source = artifact if isinstance(artifact, dict) else {}
    authority = _authority_from_artifact(source)

    errors: List[Dict[str, Any]] = []
    checks: List[Dict[str, Any]] = []

    for key, expected in sorted(REQUIRED_FALSE_CLAIMS.items()):
        actual = authority.get(key)
        passed = actual is expected
        checks.append(
            {
                "check_id": f"required_false:{key}",
                "passed": passed,
                "expected": expected,
                "actual": actual,
            }
        )
        if not passed:
            errors.append(
                {
                    "code": f"memory_authority_claim_must_be_false:{key}",
                    "message": f"External Memory may not claim {key}.",
                    "actual": actual,
                }
            )

    for key, expected in sorted(REQUIRED_TRUE_CLAIMS.items()):
        actual = authority.get(key)
        passed = actual is expected
        checks.append(
            {
                "check_id": f"required_true:{key}",
                "passed": passed,
                "expected": expected,
                "actual": actual,
            }
        )
        if not passed:
            errors.append(
                {
                    "code": f"memory_authority_claim_must_be_true:{key}",
                    "message": f"External Memory must preserve {key}=true.",
                    "actual": actual,
                }
            )

    for key in sorted(FORBIDDEN_TRUE_CLAIMS):
        actual = authority.get(key)
        passed = actual is not True
        checks.append(
            {
                "check_id": f"forbidden_true:{key}",
                "passed": passed,
                "actual": actual,
            }
        )
        if not passed:
            errors.append(
                {
                    "code": f"forbidden_memory_authority_claim:{key}",
                    "message": f"External Memory artifact illegally claimed {key}=true.",
                    "actual": actual,
                }
            )

    allowed = not errors

    return {
        "artifact_type": "external_memory_authority_guard_decision",
        "artifact_version": MEMORY_AUTHORITY_GUARD_VERSION,
        "checked_at": _utc_now_iso(),
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "authority": authority,
        "checks": checks,
        "errors": errors,
        "policy": build_memory_authority_policy(),
        "sealed": True,
    }


def apply_memory_authority_guard(artifact: Dict[str, Any]) -> Dict[str, Any]:
    source = artifact if isinstance(artifact, dict) else {}
    guarded = dict(source)
    guarded["authority"] = _authority_from_artifact(source)

    decision = evaluate_memory_authority(guarded)
    guarded["memory_authority_guard"] = decision
    guarded["sealed"] = True

    if decision.get("allowed") is not True:
        guarded["status"] = "blocked"
        guarded["blocked_reason"] = "external_memory_authority_guard_failed"

    return guarded


def assert_memory_authority_allowed(artifact: Dict[str, Any]) -> Dict[str, Any]:
    guarded = apply_memory_authority_guard(artifact)
    decision = guarded.get("memory_authority_guard", {})

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "external_memory_authority_guard_blocked",
                "decision": decision,
            }
        )

    return guarded