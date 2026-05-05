from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List


ENGINE_DRIFT_GUARD_VERSION = "v5C.2"


PROTECTED_INTERPRETATION_FIELDS = {
    "type",
    "classification",
    "direction",
    "confidence",
    "confidence_band",
    "weight",
    "weight_band",
    "summary",
    "evidence_signals",
    "constraints",
}


PROTECTED_AUTHORITY_FIELDS = {
    "can_execute",
    "can_mutate_state",
    "can_write_external_memory",
    "can_override_pm",
    "can_override_canon",
    "can_bypass_watcher",
    "can_reweight_downstream",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _extract_interpretation(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("interpretation"))


def _extract_authority(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("authority"))


def seal_engine_interpretation_for_handoff(
    engine_interpretation_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create a drift-seal snapshot for engine meaning.

    This does not grant authority. It preserves the engine's assigned meaning so
    downstream layers can prove they did not reinterpret or reweight it.
    """
    packet = deepcopy(_safe_dict(engine_interpretation_packet))
    interpretation = _extract_interpretation(packet)
    authority = _extract_authority(packet)

    protected_interpretation = {
        key: interpretation.get(key)
        for key in sorted(PROTECTED_INTERPRETATION_FIELDS)
        if key in interpretation
    }

    protected_authority = {
        key: authority.get(key)
        for key in sorted(PROTECTED_AUTHORITY_FIELDS)
        if key in authority
    }

    seal_payload = {
        "artifact_type": packet.get("artifact_type"),
        "artifact_version": packet.get("artifact_version"),
        "engine_id": packet.get("engine_id"),
        "source_research_packet_id": packet.get("source_research_packet_id"),
        "origin_authority": packet.get("origin_authority"),
        "interpretation": protected_interpretation,
        "authority": protected_authority,
        "bounded": packet.get("bounded"),
        "sealed": packet.get("sealed"),
    }

    return {
        "artifact_type": "engine_interpretation_drift_seal",
        "artifact_version": ENGINE_DRIFT_GUARD_VERSION,
        "sealed_at": _utc_now_iso(),
        "seal_hash": _sha256(seal_payload),
        "protected_fields": {
            "interpretation": sorted(PROTECTED_INTERPRETATION_FIELDS),
            "authority": sorted(PROTECTED_AUTHORITY_FIELDS),
        },
        "seal_payload": seal_payload,
        "policy": {
            "child_core_reinterpretation_allowed": False,
            "downstream_reweighting_allowed": False,
            "classification_mutation_allowed": False,
            "confidence_mutation_allowed": False,
            "direction_mutation_allowed": False,
        },
    }


def attach_drift_seal_to_handoff(handoff_packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = deepcopy(_safe_dict(handoff_packet))
    interpretation_packet = _safe_dict(packet.get("engine_interpretation_packet"))

    if not interpretation_packet:
        packet["engine_drift_seal"] = {
            "artifact_type": "engine_interpretation_drift_seal",
            "artifact_version": ENGINE_DRIFT_GUARD_VERSION,
            "sealed_at": _utc_now_iso(),
            "seal_hash": "",
            "error": "missing_engine_interpretation_packet",
            "policy": {
                "child_core_reinterpretation_allowed": False,
                "downstream_reweighting_allowed": False,
            },
        }
        return packet

    packet["engine_drift_seal"] = seal_engine_interpretation_for_handoff(
        interpretation_packet
    )
    return packet


def evaluate_engine_drift(
    *,
    original_handoff_packet: Dict[str, Any],
    candidate_handoff_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare a candidate downstream packet against the original engine seal.

    Any mutation of protected engine meaning is blocked.
    """
    original = _safe_dict(original_handoff_packet)
    candidate = _safe_dict(candidate_handoff_packet)

    original_seal = _safe_dict(original.get("engine_drift_seal"))
    if not original_seal:
        original_seal = seal_engine_interpretation_for_handoff(
            _safe_dict(original.get("engine_interpretation_packet"))
        )

    candidate_seal = seal_engine_interpretation_for_handoff(
        _safe_dict(candidate.get("engine_interpretation_packet"))
    )

    original_hash = str(original_seal.get("seal_hash", "")).strip()
    candidate_hash = str(candidate_seal.get("seal_hash", "")).strip()

    errors: List[str] = []

    if not original_hash:
        errors.append("missing_original_engine_drift_seal_hash")

    if not candidate_hash:
        errors.append("missing_candidate_engine_drift_seal_hash")

    if original_hash and candidate_hash and original_hash != candidate_hash:
        errors.append("engine_interpretation_drift_detected")

    allowed = len(errors) == 0

    return {
        "artifact_type": "engine_drift_guard_decision",
        "artifact_version": ENGINE_DRIFT_GUARD_VERSION,
        "checked_at": _utc_now_iso(),
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "errors": errors,
        "original_hash": original_hash,
        "candidate_hash": candidate_hash,
        "policy": {
            "child_core_reinterpretation_allowed": False,
            "downstream_reweighting_allowed": False,
            "classification_mutation_allowed": False,
            "confidence_mutation_allowed": False,
            "direction_mutation_allowed": False,
        },
        "message": (
            "No engine meaning drift detected."
            if allowed
            else "Engine meaning drift detected. Downstream packet blocked."
        ),
    }


def assert_no_engine_drift(
    *,
    original_handoff_packet: Dict[str, Any],
    candidate_handoff_packet: Dict[str, Any],
) -> Dict[str, Any]:
    decision = evaluate_engine_drift(
        original_handoff_packet=original_handoff_packet,
        candidate_handoff_packet=candidate_handoff_packet,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "engine_drift_guard_blocked",
                "decision": decision,
            }
        )

    return decision