from __future__ import annotations


class RosettaRefinementConsumerError(Exception):
    """Raised when Rosetta refinement consumer input artifacts are invalid."""


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RosettaRefinementConsumerError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RosettaRefinementConsumerError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RosettaRefinementConsumerError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RosettaRefinementConsumerError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RosettaRefinementConsumerError(
                f"{name} contains internal field: {key}"
            )


def _validate_rosetta_entry(entry, index):
    _require_dict(entry, f"rosetta_packet[{index}]")

    required_fields = [
        "guidance_type",
        "guidance_text",
        "source_candidate_type",
        "total_score",
        "commit_targets",
    ]

    for field in required_fields:
        if field not in entry:
            raise RosettaRefinementConsumerError(
                f"rosetta_packet[{index}] missing required field: {field}"
            )

    if not isinstance(entry["guidance_text"], str):
        raise RosettaRefinementConsumerError(
            f"rosetta_packet[{index}] guidance_text must be string"
        )

    if not isinstance(entry["total_score"], int):
        raise RosettaRefinementConsumerError(
            f"rosetta_packet[{index}] total_score must be int"
        )

    if not isinstance(entry["commit_targets"], list):
        raise RosettaRefinementConsumerError(
            f"rosetta_packet[{index}] commit_targets must be list"
        )

    return entry


def build_rosetta_refinement_receipt(refinement_consumer_packet):
    _require_dict(refinement_consumer_packet, "refinement_consumer_packet")
    _require_artifact_type(refinement_consumer_packet, "refinement_consumer_packet")

    payload = _require_payload(refinement_consumer_packet, "refinement_consumer_packet")
    _reject_internal_fields(payload, "refinement_consumer_packet")
    _require_sealed(payload, "refinement_consumer_packet")

    if "rosetta_packet" not in payload:
        raise RosettaRefinementConsumerError("missing rosetta_packet")

    rosetta_packet = payload["rosetta_packet"]

    if not isinstance(rosetta_packet, list):
        raise RosettaRefinementConsumerError("rosetta_packet must be list")

    validated_entries = [
        _validate_rosetta_entry(entry, index)
        for index, entry in enumerate(rosetta_packet)
    ]

    consumer_notes = []
    if not validated_entries:
        consumer_notes.append("no_rosetta_guidance_available")

    return {
        "artifact_type": "rosetta_refinement_receipt",
        "payload": {
            "issuing_authority": "RUNTIME_ROSETTA_REFINEMENT_CONSUMER",
            "source_artifact_type": "refinement_consumer_packet",
            "consumed_count": len(validated_entries),
            "rosetta_guidance": validated_entries,
            "consumer_notes": consumer_notes,
            "sealed": True,
        },
    }