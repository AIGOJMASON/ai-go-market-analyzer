from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


CROSS_CORE_ENFORCEMENT_VERSION = "v6c.1"
ARTIFACT_TYPE = "cross_core_enforcement_decision"

CANONICAL_CHAIN = ["oracle", "decision", "risk", "router", "comply"]

ALLOWED_PATHS = {
    ("oracle", "decision"),
    ("decision", "risk"),
    ("risk", "router"),
    ("router", "comply"),
    ("assumption", "oracle"),
    ("assumption", "decision"),
    ("assumption", "risk"),
    ("assumption", "router"),
    ("assumption", "comply"),
}

REQUIRED_GOVERNANCE_TRUE_FIELDS = (
    "watcher_valid",
    "state_valid",
    "execution_gate_allowed",
    "mutation_guard_valid",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _reason(code: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "severity": "blocker",
        "details": details or {},
    }


def _check(check_id: str, passed: bool, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": passed,
        "details": details or {},
    }


def _source_type(packet: Dict[str, Any]) -> str:
    source = packet.get("source")
    if isinstance(source, dict):
        return _clean(source.get("source_type")).lower()
    return _clean(source).lower()


def _target_service(packet: Dict[str, Any]) -> str:
    target = packet.get("target")
    if isinstance(target, dict):
        return _clean(target.get("target_service")).lower()
    return _clean(target).lower()


def _packet_id(packet: Dict[str, Any]) -> str:
    return _clean(packet.get("packet_id"))


def _governance_refs(packet: Dict[str, Any]) -> Dict[str, Any]:
    source = _as_dict(packet.get("source"))
    refs = _as_dict(source.get("governance_refs"))

    if not refs:
        refs = _as_dict(packet.get("governance_refs"))

    return refs


def _packet_is_governed(packet: Dict[str, Any]) -> bool:
    refs = _governance_refs(packet)

    for field in REQUIRED_GOVERNANCE_TRUE_FIELDS:
        if refs.get(field) is not True:
            return False

    return True


def _packet_shape_valid(packet: Dict[str, Any]) -> bool:
    return (
        _clean(packet.get("artifact_type")) == "contractor_pm_coupling_packet"
        and bool(_packet_id(packet))
        and bool(_source_type(packet))
        and bool(_target_service(packet))
    )


def _link(packet: Dict[str, Any]) -> Tuple[str, str]:
    return (_source_type(packet), _target_service(packet))


def _build_chain_summary(packets: List[Dict[str, Any]]) -> Dict[str, Any]:
    links = []
    canonical_positions = []

    for packet in packets:
        source, target = _link(packet)
        links.append(
            {
                "packet_id": _packet_id(packet),
                "source": source,
                "target": target,
                "path": f"{source}->{target}",
            }
        )

        if source in CANONICAL_CHAIN:
            canonical_positions.append(CANONICAL_CHAIN.index(source))
        if target in CANONICAL_CHAIN:
            canonical_positions.append(CANONICAL_CHAIN.index(target))

    return {
        "canonical_chain": CANONICAL_CHAIN,
        "link_count": len(links),
        "links": links,
        "canonical_positions": canonical_positions,
    }


def _validate_packets_present(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    passed = bool(packets)
    checks.append(_check("cross_core_packets_present", passed))

    if not passed:
        reasons.append(
            _reason(
                "cross_core_packets_missing",
                "Cross-core enforcement requires at least one coupling packet.",
            )
        )


def _validate_packet_shapes(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    for index, packet in enumerate(packets):
        passed = _packet_shape_valid(packet)
        checks.append(
            _check(
                "cross_core_packet_shape_valid",
                passed,
                {"index": index, "packet_id": _packet_id(packet)},
            )
        )

        if not passed:
            reasons.append(
                _reason(
                    "invalid_cross_core_packet_shape",
                    "Coupling packet is missing required shape fields.",
                    {"index": index, "packet": packet},
                )
            )


def _validate_duplicate_packets(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    seen = set()

    for packet in packets:
        pid = _packet_id(packet)
        if not pid:
            continue

        duplicate = pid in seen
        checks.append(
            _check(
                "cross_core_packet_not_duplicate",
                not duplicate,
                {"packet_id": pid},
            )
        )

        if duplicate:
            reasons.append(
                _reason(
                    "duplicate_cross_core_packet",
                    "Duplicate cross-core coupling packet detected.",
                    {"packet_id": pid},
                )
            )

        seen.add(pid)


def _validate_allowed_paths(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    for packet in packets:
        source, target = _link(packet)
        allowed = (source, target) in ALLOWED_PATHS

        checks.append(
            _check(
                "cross_core_path_allowed",
                allowed,
                {
                    "packet_id": _packet_id(packet),
                    "source": source,
                    "target": target,
                    "path": f"{source}->{target}",
                },
            )
        )

        if not allowed:
            reasons.append(
                _reason(
                    "illegal_cross_core_path",
                    "Cross-core packet attempts an illegal source to target path.",
                    {
                        "packet_id": _packet_id(packet),
                        "source": source,
                        "target": target,
                    },
                )
            )


def _validate_governed_packets(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    for packet in packets:
        refs = _governance_refs(packet)
        governed = _packet_is_governed(packet)

        checks.append(
            _check(
                "cross_core_packet_governed",
                governed,
                {
                    "packet_id": _packet_id(packet),
                    "governance_refs": refs,
                },
            )
        )

        if not governed:
            reasons.append(
                _reason(
                    "cross_core_packet_not_governed",
                    "Cross-core packet lacks required governance refs.",
                    {
                        "packet_id": _packet_id(packet),
                        "required_true_fields": list(REQUIRED_GOVERNANCE_TRUE_FIELDS),
                        "governance_refs": refs,
                    },
                )
            )


def _validate_chain_order(
    packets: List[Dict[str, Any]],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    last_position = -1

    for packet in packets:
        source, target = _link(packet)

        if source == "assumption":
            continue

        if source not in CANONICAL_CHAIN or target not in CANONICAL_CHAIN:
            continue

        source_position = CANONICAL_CHAIN.index(source)
        target_position = CANONICAL_CHAIN.index(target)

        ordered = source_position <= target_position and source_position >= last_position

        checks.append(
            _check(
                "cross_core_chain_order_valid",
                ordered,
                {
                    "packet_id": _packet_id(packet),
                    "source": source,
                    "target": target,
                    "last_position": last_position,
                    "source_position": source_position,
                    "target_position": target_position,
                },
            )
        )

        if not ordered:
            reasons.append(
                _reason(
                    "cross_core_chain_order_violation",
                    "Cross-core packet order violates canonical causal sequence.",
                    {
                        "packet_id": _packet_id(packet),
                        "canonical_chain": CANONICAL_CHAIN,
                        "source": source,
                        "target": target,
                    },
                )
            )

        last_position = max(last_position, source_position)


def enforce_cross_core_chain(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "cross_core_enforcement",
) -> Dict[str, Any]:
    source_payload = _as_dict(payload)
    packets = _as_list(source_payload.get("packets"))

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []

    _validate_packets_present(packets, checks, reasons)
    _validate_packet_shapes(packets, checks, reasons)
    _validate_duplicate_packets(packets, checks, reasons)
    _validate_allowed_paths(packets, checks, reasons)
    _validate_governed_packets(packets, checks, reasons)
    _validate_chain_order(packets, checks, reasons)

    blocked = bool(reasons)

    output: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": CROSS_CORE_ENFORCEMENT_VERSION,
        "created_at": _utc_now_iso(),
        "profile": _clean(profile),
        "action": _clean(action),
        "actor": _clean(actor) or "cross_core_enforcement",
        "status": "blocked" if blocked else "allowed",
        "decision": "block" if blocked else "allow",
        "allowed": not blocked,
        "blocked": blocked,
        "checks": checks,
        "reasons": reasons,
        "chain": _build_chain_summary(packets),
        "authority": {
            "watcher_owned": True,
            "cross_core_gate": True,
            "may_block_propagation": True,
            "may_execute": False,
            "may_mutate_state": False,
            "may_call_services": False,
        },
        "constraints": {
            "decision_only": True,
            "no_direct_execution": True,
            "no_direct_state_mutation": True,
            "no_lateral_service_call": True,
            "invalid_chain_blocks": True,
            "ungoverned_packet_blocks": True,
            "illegal_path_blocks": True,
            "out_of_order_chain_blocks": True,
        },
        "sealed": True,
    }

    output["cross_core_decision_hash"] = _hash(
        {
            key: value
            for key, value in output.items()
            if key != "cross_core_decision_hash"
        }
    )

    return output


def assert_cross_core_allowed(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "cross_core_enforcement",
) -> Dict[str, Any]:
    decision = enforce_cross_core_chain(
        payload=payload,
        action=action,
        profile=profile,
        actor=actor,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "cross_core_enforcement_blocked",
                "decision": decision,
            }
        )

    return decision