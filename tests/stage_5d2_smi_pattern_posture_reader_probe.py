from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.awareness.smi_pattern_posture_reader import (
    build_smi_pattern_posture_packet,
    summarize_smi_pattern_posture,
)


PHASE = "5D.2"
PROBE_ID = "stage_5d2_smi_pattern_posture_reader_probe"


FORBIDDEN_TRUE_PATHS = [
    ("authority", "can_execute"),
    ("authority", "can_mutate_state"),
    ("authority", "can_override_governance"),
    ("authority", "can_override_watcher"),
    ("authority", "can_override_execution_gate"),
    ("authority", "can_route_work"),
    ("authority", "execution_allowed"),
    ("authority", "mutation_allowed"),
    ("use_policy", "may_change_execution_gate"),
    ("use_policy", "may_change_watcher"),
    ("use_policy", "may_change_state"),
    ("use_policy", "may_write_decisions"),
    ("use_policy", "may_dispatch_actions"),
    ("use_policy", "may_activate_child_cores"),
]


def _assert_no_authority(packet: Dict[str, Any]) -> None:
    for block_name, key in FORBIDDEN_TRUE_PATHS:
        block = packet.get(block_name, {})
        assert isinstance(block, dict), f"{block_name} must be dict"
        assert block.get(key) is False, f"{block_name}.{key} must be false"

    validation = packet.get("validation", {})
    assert validation.get("valid") is True, validation
    assert validation.get("authority_violations") == [], validation


def _sample_system_smi_history() -> List[Dict[str, Any]]:
    return [
        {
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-alpha",
                "phase_id": "phase-demo",
                "interpretation_class": "governed_probe",
            },
        },
        {
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-alpha",
                "phase_id": "phase-demo",
                "interpretation_class": "governed_probe",
            },
        },
        {
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "market_analyzer_v1",
                "project_id": "project-beta",
                "phase_id": "phase-review",
                "interpretation_class": "advisory_signal",
            },
        },
    ]


def _build_pattern_case() -> Dict[str, Any]:
    return build_smi_pattern_posture_packet(
        pm_continuity_state={
            "artifact_type": "pm_continuity_state",
            "posture": "observed",
            "signals": [
                {
                    "signal_type": "route_observed",
                    "child_core_id": "contractor_builder_v1",
                }
            ],
        },
        pm_change_ledger={
            "changes": [
                {
                    "change_id": "change-001",
                    "status": "observed",
                }
            ]
        },
        pm_unresolved_queue={},
        system_smi_latest={
            "artifact_type": "system_smi_record",
            "sealed": True,
            "continuity": {
                "child_core_id": "contractor_builder_v1",
                "project_id": "project-alpha",
                "phase_id": "phase-demo",
                "interpretation_class": "governed_probe",
            },
            "system_brain_signal": {
                "available": True,
                "posture": "advisory_continuity_only",
            },
        },
        system_smi_history=_sample_system_smi_history(),
    )


def _build_cautious_case() -> Dict[str, Any]:
    return build_smi_pattern_posture_packet(
        pm_continuity_state={
            "artifact_type": "pm_continuity_state",
            "posture": "observed",
            "signals": [],
        },
        pm_change_ledger={},
        pm_unresolved_queue={
            "items": [
                {
                    "item_id": "unresolved-001",
                    "status": "open",
                }
            ]
        },
        system_smi_latest={},
        system_smi_history=[],
    )


def _build_cold_start_case() -> Dict[str, Any]:
    return build_smi_pattern_posture_packet(
        pm_continuity_state={},
        pm_change_ledger={},
        pm_unresolved_queue={},
        system_smi_latest={},
        system_smi_history=[],
    )


def run_probe() -> Dict[str, Any]:
    pattern_packet = _build_pattern_case()
    cautious_packet = _build_cautious_case()
    cold_start_packet = _build_cold_start_case()

    _assert_no_authority(pattern_packet)
    _assert_no_authority(cautious_packet)
    _assert_no_authority(cold_start_packet)

    assert pattern_packet["artifact_type"] == "smi_pattern_posture_packet"
    assert pattern_packet["sealed"] is True
    assert pattern_packet["summary"]["posture"] == "pattern_observed"
    assert pattern_packet["summary"]["pattern_signal_count"] >= 2
    assert pattern_packet["summary"]["pm_signal_count"] >= 1
    assert pattern_packet["summary"]["system_smi_signal_count"] >= 1

    pattern_types = {
        signal.get("pattern_type")
        for signal in pattern_packet.get("pattern_signals", [])
    }
    assert "continuity_history_available" in pattern_types
    assert "recurring_child_core_id" in pattern_types
    assert "recurring_project_id" in pattern_types

    assert cautious_packet["summary"]["posture"] == "cautious"
    cautious_types = {
        signal.get("pattern_type")
        for signal in cautious_packet.get("pattern_signals", [])
    }
    assert "unresolved_pm_queue_present" in cautious_types

    assert cold_start_packet["summary"]["posture"] == "cold_start"
    cold_types = {
        signal.get("pattern_type")
        for signal in cold_start_packet.get("pattern_signals", [])
    }
    assert "cold_start" in cold_types

    compact_summary = summarize_smi_pattern_posture(pattern_packet)
    assert compact_summary["advisory_only"] is True
    assert compact_summary["execution_allowed"] is False
    assert compact_summary["mutation_allowed"] is False

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "pattern_case": {
            "posture": pattern_packet["summary"]["posture"],
            "pattern_signal_count": pattern_packet["summary"]["pattern_signal_count"],
            "authority_valid": pattern_packet["validation"]["valid"],
        },
        "cautious_case": {
            "posture": cautious_packet["summary"]["posture"],
            "pattern_signal_count": cautious_packet["summary"]["pattern_signal_count"],
            "authority_valid": cautious_packet["validation"]["valid"],
        },
        "cold_start_case": {
            "posture": cold_start_packet["summary"]["posture"],
            "pattern_signal_count": cold_start_packet["summary"]["pattern_signal_count"],
            "authority_valid": cold_start_packet["validation"]["valid"],
        },
        "summary_contract": compact_summary,
        "next": {
            "phase": "5D.3",
            "recommended_step": "Build System Brain aggregator that consumes SMI posture, temporal awareness, pattern recognition, and cross-run intelligence as advisory-only intelligence.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D2_SMI_PATTERN_POSTURE_READER_PROBE: PASS")
    print(result)