from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from AI_GO.core.smi.system_smi import (
    build_system_smi_record,
    persist_system_smi_record,
)
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


ROOT_INTELLIGENCE_SPINE_VERSION = "v1.1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_bool(value: Any) -> bool:
    return value is True


def _run_external_memory_if_curated(
    *,
    handoff_packet: dict[str, Any],
    curation_approved: bool,
) -> dict[str, Any]:
    if not curation_approved:
        return {
            "status": "skipped",
            "reason": "curation_not_approved",
            "policy": {
                "external_memory_is_recycling_and_refinement_only": True,
                "raw_input_persistence_allowed": False,
                "requires_engine_curated_packet": True,
            },
        }

    try:
        from AI_GO.EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
            run_external_memory_runtime_path,
        )

        result = run_external_memory_runtime_path(
            _safe_dict(handoff_packet.get("child_core_handoff")).get("packet", {})
        )
        result["policy"] = {
            "external_memory_is_recycling_and_refinement_only": True,
            "raw_input_persistence_allowed": False,
            "requires_engine_curated_packet": True,
        }
        return result

    except Exception as exc:
        return {
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
            "policy": {
                "external_memory_is_recycling_and_refinement_only": True,
                "fail_closed": True,
            },
        }


def run_root_intelligence_spine(
    *,
    research_packet: dict[str, Any],
    curation_approved: bool = False,
) -> dict[str, Any]:
    trace_id = (
        "root_spine_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid4().hex[:10]}"
    )

    handoff_packet = curate_research_packet_for_child_cores(research_packet)

    provisional = {
        "artifact_type": "root_intelligence_spine_packet",
        "artifact_version": ROOT_INTELLIGENCE_SPINE_VERSION,
        "trace_id": trace_id,
        "generated_at": _utc_now_iso(),
        "research_packet": research_packet,
        "engine_handoff_packet": handoff_packet,
    }

    smi_record = build_system_smi_record(source_packet=provisional)
    smi_persistence = persist_system_smi_record(smi_record)

    external_memory_result = _run_external_memory_if_curated(
        handoff_packet=handoff_packet,
        curation_approved=curation_approved,
    )

    return {
        **provisional,
        "phase": "Phase 5A.1",
        "mode": "provider_extraction_root_research_spine",
        "sealed": True,
        "authority": {
            "research_core_required": True,
            "engines_required_before_child_core": True,
            "smi_system_wide": True,
            "external_memory_curated_only": True,
            "provider_clients_inside_child_core_allowed": False,
            "raw_provider_payload_to_child_core_allowed": False,
            "ai_connected": False,
            "can_execute": False,
            "can_mutate_child_core_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
        },
        "spine_order": [
            "provider_fetch",
            "RESEARCH_CORE_pre_weight",
            "engines_curated_handoff",
            "child_core_optional_read",
            "SMI_continuity",
            "EXTERNAL_MEMORY_optional_curated_only",
        ],
        "smi_record": smi_record,
        "smi_persistence": smi_persistence,
        "external_memory_result": external_memory_result,
        "summary": {
            "research_valid": bool(_safe_dict(research_packet.get("screening")).get("valid")),
            "pre_weight": _safe_dict(research_packet.get("trust")).get("pre_weight"),
            "trust_class": _safe_dict(research_packet.get("trust")).get("trust_class"),
            "handoff_allowed": _safe_dict(handoff_packet.get("child_core_handoff")).get("allowed"),
            "targets": _safe_dict(handoff_packet.get("child_core_handoff")).get("targets", []),
            "smi_recorded": smi_persistence.get("status") == "persisted",
            "external_memory_status": external_memory_result.get("status"),
        },
    }