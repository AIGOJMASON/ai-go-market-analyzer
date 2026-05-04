from __future__ import annotations

from typing import Any, Dict

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)
from AI_GO.core.awareness.smi_pattern_posture_reader import (
    build_smi_pattern_posture_packet,
)
from AI_GO.core.system_brain.system_brain import (
    build_system_brain_context,
    summarize_system_brain_context,
)


PHASE = "5D.5"
PROBE_ID = "stage_5d5_full_system_brain_regression_probe"


FORBIDDEN_AUTHORITY_TRUE = [
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_escalate_automatically",
    "can_route_work",
    "can_block_request",
    "can_allow_request",
    "execution_allowed",
    "mutation_allowed",
]


FORBIDDEN_USE_TRUE = [
    "may_change_canon_decision",
    "may_change_execution_gate",
    "may_change_watcher",
    "may_change_state",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
    "may_override_governance",
]


def _assert_false_flags(block: Dict[str, Any], keys: list[str], block_name: str) -> None:
    for key in keys:
        if key in block:
            assert block.get(key) is False, f"{block_name}.{key} must remain false"


def _assert_authority_locked(packet: Dict[str, Any]) -> None:
    authority = packet.get("authority", {})
    use_policy = packet.get("use_policy", {})

    assert isinstance(authority, dict), "authority must be dict"
    assert isinstance(use_policy, dict), "use_policy must be dict"

    _assert_false_flags(authority, FORBIDDEN_AUTHORITY_TRUE, "authority")
    _assert_false_flags(use_policy, FORBIDDEN_USE_TRUE, "use_policy")

    assert authority.get("can_execute", False) is False
    assert authority.get("can_mutate_state", False) is False
    assert authority.get("can_override_governance", False) is False


def _sample_smi_history() -> list[Dict[str, Any]]:
    return [
        {
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-regression",
                "phase_id": "phase-system-brain",
                "interpretation_class": "system_brain_visibility",
            },
        },
        {
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-regression",
                "phase_id": "phase-system-brain",
                "interpretation_class": "system_brain_visibility",
            },
        },
    ]


def _build_smi_reader_packet() -> Dict[str, Any]:
    return build_smi_pattern_posture_packet(
        pm_continuity_state={
            "artifact_type": "pm_continuity_state",
            "posture": "observed",
            "signals": [
                {
                    "signal_type": "system_brain_regression_signal",
                    "source": "stage_5d5_probe",
                }
            ],
        },
        pm_change_ledger={},
        pm_unresolved_queue={},
        system_smi_latest={
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-regression",
                "phase_id": "phase-system-brain",
                "interpretation_class": "system_brain_visibility",
            },
        },
        system_smi_history=_sample_smi_history(),
    )


def _build_system_brain_context_from_smi(
    smi_packet: Dict[str, Any],
) -> Dict[str, Any]:
    return build_system_brain_context(
        smi_posture_packet=smi_packet,
        temporal_awareness_packet={
            "status": "ok",
            "artifact_type": "temporal_awareness_packet",
            "sealed": True,
            "summary": {
                "temporal_posture": "stable",
            },
        },
        pattern_recognition_packet={
            "status": "ok",
            "artifact_type": "pattern_recognition_packet",
            "sealed": True,
            "summary": {
                "pattern_signal_count": 1,
            },
        },
        unified_awareness_packet={
            "status": "ok",
            "artifact_type": "unified_system_awareness_packet",
            "sealed": True,
            "summary": {
                "system_posture": "stable",
                "risk_posture": "stable",
            },
        },
        cross_run_intelligence_packet={
            "status": "ok",
            "artifact_type": "cross_run_intelligence_packet",
            "sealed": True,
            "summary": {
                "drift": "stable",
                "persistent_signal_count": 1,
            },
        },
    )


def _assert_smi_reader(packet: Dict[str, Any]) -> None:
    assert packet["status"] == "ok"
    assert packet["artifact_type"] == "smi_pattern_posture_packet"
    assert packet["sealed"] is True
    assert packet["validation"]["valid"] is True
    assert packet["summary"]["posture"] == "pattern_observed"
    assert packet["summary"]["pattern_signal_count"] >= 2
    _assert_authority_locked(packet)


def _assert_system_brain_context(packet: Dict[str, Any]) -> None:
    assert packet["status"] == "ok"
    assert packet["artifact_type"] == "system_brain_context"
    assert packet["mode"] == "read_only"
    assert packet["sealed"] is True
    assert packet["validation"]["valid"] is True
    assert packet["summary"]["risk_posture"] == "stable_observed"
    assert packet["summary"]["smi_posture"] == "pattern_observed"
    assert packet["summary"]["pattern_signal_count"] >= 1
    assert "smi_pattern_posture" in packet["source_surfaces"]
    assert "cross_run_intelligence" in packet["source_surfaces"]
    _assert_authority_locked(packet)

    compact = summarize_system_brain_context(packet)
    assert compact["advisory_only"] is True
    assert compact["execution_allowed"] is False
    assert compact["mutation_allowed"] is False


def _assert_operator_surface(surface: Dict[str, Any]) -> None:
    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True
    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert isinstance(surface["plain_summary"], str)
    assert surface["plain_summary"]
    assert isinstance(surface["operator_cards"], list)
    assert len(surface["operator_cards"]) >= 1
    assert isinstance(surface["what_to_watch"], list)
    assert len(surface["what_to_watch"]) >= 1

    assert "system_brain" in surface
    assert "system_context_summary" in surface["system_brain"]
    assert "source_surfaces" in surface
    assert "system_brain_context" in surface["source_surfaces"]

    system_context = surface["source_surfaces"]["system_brain_context"]
    assert system_context["artifact_type"] == "system_brain_context"
    assert system_context["mode"] == "read_only"
    assert system_context["sealed"] is True

    _assert_authority_locked(surface)


def _assert_api_surface(client: TestClient) -> Dict[str, Any]:
    response = client.get("/contractor-builder/system-brain/surface?limit=500")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    surface = payload["surface"]
    _assert_operator_surface(surface)

    return payload


def _assert_api_summary(client: TestClient) -> Dict[str, Any]:
    response = client.get("/contractor-builder/system-brain/summary?limit=500")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    assert isinstance(payload["plain_summary"], str)
    assert payload["plain_summary"]
    assert isinstance(payload["operator_cards"], list)
    assert isinstance(payload["what_to_watch"], list)
    assert isinstance(payload["system_brain"], dict)

    _assert_authority_locked(payload)

    return payload


def _assert_health_route(client: TestClient) -> Dict[str, Any]:
    response = client.get("/contractor-builder/health")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "advisory"
    assert payload["approval_required"] is True
    assert payload["execution_allowed"] is False
    assert payload["routes"]["system_brain"] is True

    return payload


def run_probe() -> Dict[str, Any]:
    smi_packet = _build_smi_reader_packet()
    _assert_smi_reader(smi_packet)

    system_brain_context = _build_system_brain_context_from_smi(smi_packet)
    _assert_system_brain_context(system_brain_context)

    operator_surface = build_operator_system_brain_surface(limit=500)
    _assert_operator_surface(operator_surface)

    client = TestClient(app)
    health_payload = _assert_health_route(client)
    api_surface_payload = _assert_api_surface(client)
    api_summary_payload = _assert_api_summary(client)

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "chain_validated": [
            "smi_pattern_posture_reader",
            "system_brain_context",
            "operator_system_brain_surface",
            "contractor_system_brain_api_surface",
            "contractor_system_brain_api_summary",
            "contractor_builder_health_route",
        ],
        "smi_reader": {
            "posture": smi_packet["summary"]["posture"],
            "pattern_signal_count": smi_packet["summary"]["pattern_signal_count"],
            "authority_valid": smi_packet["validation"]["valid"],
        },
        "system_brain_context": {
            "risk_posture": system_brain_context["summary"]["risk_posture"],
            "smi_posture": system_brain_context["summary"]["smi_posture"],
            "pattern_signal_count": system_brain_context["summary"]["pattern_signal_count"],
            "authority_valid": system_brain_context["validation"]["valid"],
        },
        "operator_surface": {
            "surface_version": operator_surface["artifact_version"],
            "operator_cards": len(operator_surface["operator_cards"]),
            "watch_items": len(operator_surface["what_to_watch"]),
            "system_context_visible": "system_context_summary"
            in operator_surface["system_brain"],
        },
        "api": {
            "health_system_brain_route": health_payload["routes"]["system_brain"],
            "surface_visible": api_surface_payload["status"] == "ok",
            "summary_visible": api_summary_payload["status"] == "ok",
            "execution_allowed": False,
            "mutation_allowed": False,
        },
        "authority_confirmed": {
            "smi_reader": "advisory_only",
            "system_brain_context": "read_only_advisory_only",
            "operator_surface": "operator_read_only_advisory_only",
            "api": "read_only_no_execution_no_mutation",
        },
        "next": {
            "phase": "5D complete",
            "recommended_step": "Update Northstar handoff, then proceed to 5E State Authority when ready.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D5_FULL_SYSTEM_BRAIN_REGRESSION_PROBE: PASS")
    print(result)