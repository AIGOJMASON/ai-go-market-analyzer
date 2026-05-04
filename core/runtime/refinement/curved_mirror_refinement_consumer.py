from __future__ import annotations


class CurvedMirrorRefinementConsumerError(Exception):
    """Raised when Curved Mirror refinement consumer input artifacts are invalid."""


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise CurvedMirrorRefinementConsumerError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise CurvedMirrorRefinementConsumerError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise CurvedMirrorRefinementConsumerError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise CurvedMirrorRefinementConsumerError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise CurvedMirrorRefinementConsumerError(
                f"{name} contains internal field: {key}"
            )


def _validate_curved_mirror_entry(entry, index):
    _require_dict(entry, f"curved_mirror_packet[{index}]")

    required_fields = [
        "signal_type",
        "signal_value",
        "total_score",
        "commit_targets",
        "source_candidate_type",
    ]

    for field in required_fields:
        if field not in entry:
            raise CurvedMirrorRefinementConsumerError(
                f"curved_mirror_packet[{index}] missing required field: {field}"
            )

    if not isinstance(entry["total_score"], int):
        raise CurvedMirrorRefinementConsumerError(
            f"curved_mirror_packet[{index}] total_score must be int"
        )

    if not isinstance(entry["commit_targets"], list):
        raise CurvedMirrorRefinementConsumerError(
            f"curved_mirror_packet[{index}] commit_targets must be list"
        )

    return entry


def build_curved_mirror_refinement_receipt(refinement_consumer_packet):
    _require_dict(refinement_consumer_packet, "refinement_consumer_packet")
    _require_artifact_type(refinement_consumer_packet, "refinement_consumer_packet")

    payload = _require_payload(refinement_consumer_packet, "refinement_consumer_packet")
    _reject_internal_fields(payload, "refinement_consumer_packet")
    _require_sealed(payload, "refinement_consumer_packet")

    if "curved_mirror_packet" not in payload:
        raise CurvedMirrorRefinementConsumerError("missing curved_mirror_packet")

    curved_mirror_packet = payload["curved_mirror_packet"]

    if not isinstance(curved_mirror_packet, list):
        raise CurvedMirrorRefinementConsumerError("curved_mirror_packet must be list")

    validated_entries = [
        _validate_curved_mirror_entry(entry, index)
        for index, entry in enumerate(curved_mirror_packet)
    ]

    consumer_notes = []
    if not validated_entries:
        consumer_notes.append("no_curved_mirror_signals_available")

    return {
        "artifact_type": "curved_mirror_refinement_receipt",
        "payload": {
            "issuing_authority": "RUNTIME_CURVED_MIRROR_REFINEMENT_CONSUMER",
            "source_artifact_type": "refinement_consumer_packet",
            "consumed_count": len(validated_entries),
            "curved_mirror_signals": validated_entries,
            "consumer_notes": consumer_notes,
            "sealed": True,
        },
    }