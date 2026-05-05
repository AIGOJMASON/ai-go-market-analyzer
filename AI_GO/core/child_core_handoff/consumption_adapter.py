from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


CHILD_CORE_CONSUMPTION_ADAPTER_VERSION = "v1.0"


class ChildCoreConsumptionAdapterError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _assert_engine_handoff_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise ChildCoreConsumptionAdapterError("handoff_packet_must_be_dict")

    if packet.get("artifact_type") != "curated_child_core_handoff_packet":
        raise ChildCoreConsumptionAdapterError(
            f"invalid_artifact_type:{packet.get('artifact_type')}"
        )

    if packet.get("sealed") is not True:
        raise ChildCoreConsumptionAdapterError("handoff_packet_must_be_sealed")

    authority = _safe_dict(packet.get("authority"))
    if authority.get("authority_id") != "engines":
        raise ChildCoreConsumptionAdapterError("handoff_must_come_from_engines")

    if authority.get("curates_before_child_core") is not True:
        raise ChildCoreConsumptionAdapterError("missing_curates_before_child_core_flag")

    if authority.get("can_execute") is not False:
        raise ChildCoreConsumptionAdapterError("engine_handoff_can_execute_must_be_false")

    if authority.get("can_mutate_child_core") is not False:
        raise ChildCoreConsumptionAdapterError(
            "engine_handoff_can_mutate_child_core_must_be_false"
        )


def build_child_core_consumption_packet(
    *,
    child_core_id: str,
    engine_handoff_packet: dict[str, Any],
) -> dict[str, Any]:
    clean_child_core_id = _safe_str(child_core_id)
    if not clean_child_core_id:
        raise ChildCoreConsumptionAdapterError("child_core_id_required")

    _assert_engine_handoff_packet(engine_handoff_packet)

    handoff = _safe_dict(engine_handoff_packet.get("child_core_handoff"))
    targets = _safe_list(handoff.get("targets"))
    curated_packet = _safe_dict(handoff.get("packet"))

    if clean_child_core_id not in targets:
        raise ChildCoreConsumptionAdapterError(
            f"child_core_not_authorized_for_handoff:{clean_child_core_id}"
        )

    if handoff.get("allowed") is not True:
        raise ChildCoreConsumptionAdapterError("handoff_not_allowed")

    if not curated_packet:
        raise ChildCoreConsumptionAdapterError("missing_curated_child_core_packet")

    adapter_id = (
        "child_core_consumption_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid4().hex[:10]}"
    )

    return {
        "artifact_type": "child_core_consumption_packet",
        "artifact_version": CHILD_CORE_CONSUMPTION_ADAPTER_VERSION,
        "adapter_id": adapter_id,
        "generated_at": _utc_now_iso(),
        "sealed": True,
        "child_core_id": clean_child_core_id,
        "authority": {
            "authority_id": "child_core_consumption_adapter",
            "receives_engine_curated_only": True,
            "raw_provider_payload_allowed": False,
            "raw_research_packet_allowed": False,
            "can_fetch_provider": False,
            "can_execute": False,
            "can_mutate_root_state": False,
            "can_override_engines": False,
            "can_override_research_core": False,
            "can_override_governance": False,
        },
        "source": {
            "engine_handoff_artifact_type": engine_handoff_packet.get("artifact_type"),
            "engine_handoff_generated_at": engine_handoff_packet.get("generated_at"),
            "research_packet_id": _safe_dict(engine_handoff_packet.get("source")).get(
                "research_packet_id"
            ),
            "pre_weight": curated_packet.get("pre_weight"),
            "trust_class": curated_packet.get("trust_class"),
            "interpretation_class": curated_packet.get("interpretation_class"),
        },
        "curated_input": curated_packet,
        "use_policy": {
            "child_core_may_read": True,
            "child_core_may_display": True,
            "child_core_may_use_as_context": True,
            "child_core_may_execute": False,
            "child_core_may_mutate_provider_truth": False,
            "child_core_may_write_external_memory": False,
            "child_core_may_bypass_pm": False,
        },
    }