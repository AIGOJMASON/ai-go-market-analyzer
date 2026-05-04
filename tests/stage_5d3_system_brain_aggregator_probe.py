from __future__ import annotations

from typing import Any, Dict

from AI_GO.core.system_brain.system_brain import (
    build_system_brain_context,
    summarize_system_brain_context,
)


PHASE = "5D.3"
PROBE_ID = "stage_5d3_system_brain_aggregator_probe"


FORBIDDEN_AUTHORITY_TRUE = [
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_escalate_automatically",
    "can_route_work",
    "execution_allowed",
    "mutation_allowed",
]


FORBIDDEN_USE_TRUE = [
    "may_change_execution_gate",
    "may_change_watcher",
    "may_change_state",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
    "may_override_governance",
]


def _assert_no_authority(packet: Dict[str, Any]) -> None:
    authority = packet["authority"]
    assert authority["mode"] == "advisory_only"
    assert authority["read_only"] is True
    assert authority["advisory_only"] is True

    for key in FORBIDDEN_AUTHORITY_TRUE:
        assert authority.get(key) is False, f"authority.{key} must remain false"

    use_policy = packet["use_policy"]
    assert use_policy["operator_may_read"] is True
    assert use_policy["pm_may_read"] is True
    assert use_policy["may_display_in_dashboard"] is True

    for key in FORBIDDEN_USE_TRUE:
        assert use_policy.get(key) is False, f"use_policy.{key} must remain false"

    validation = packet["validation"]
    assert validation["valid"] is True, validation
    assert validation["authority_violations"] == [], validation


def _sample_smi_pattern_posture(posture: str = "pattern_observed") -> Dict[str, Any]:
    return {
        "status": "ok",
        "artifact_type": "smi_pattern_posture_packet",
        "sealed": True,
        "summary": {
            "posture": posture,
            "plain_summary": "SMI pattern summary.",
            "pattern_signal_count": 3,
            "pm_signal_count": 1,
            "system_smi_signal_count": 2,
        },
        "pattern_signals": [
            {
                "pattern_type": "recurring_child_core_id",
                "severity": "observe",
                "count": 2,
                "advisory_only": True,
            }
        ],
        "authority": {
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_governance": False,
        },
    }


def _sample_temporal_awareness() -> Dict[str, Any]:
    return {
        "status": "ok",
        "artifact_type": "temporal_awareness_packet",
        "sealed": True,
        "summary": {
            "temporal_posture": "stable",
            "window_status": "available",
        },
    }


def _sample_pattern_recognition() -> Dict[str, Any]:
    return {
        "status": "ok",
        "artifact_type": "pattern_recognition_packet",
        "sealed": True,
        "summary": {
            "pattern_signal_count": 2,
            "pattern_count": 2,
        },
    }


def _sample_unified_awareness(posture: str = "stable") -> Dict[str, Any]:
    return {
        "status": "ok",
        "artifact_type": "unified_system_awareness_packet",
        "sealed": True,
        "summary": {
            "system_posture": posture,
            "risk_posture": posture,
        },
    }


def _sample_cross_run(drift: str = "stable") -> Dict[str, Any]:
    return {
        "status": "ok",
        "artifact_type": "cross_run_intelligence_packet",
        "sealed": True,
        "summary": {
            "drift": drift,
            "persistent_signal_count": 1,
        },
    }


def _build_stable_case() -> Dict[str, Any]:
    return build_system_brain_context(
        smi_posture_packet=_sample_smi_pattern_posture("pattern_observed"),
        temporal_awareness_packet=_sample_temporal_awareness(),
        pattern_recognition_packet=_sample_pattern_recognition(),
        unified_awareness_packet=_sample_unified_awareness("stable"),
        cross_run_intelligence_packet=_sample_cross_run("stable"),
    )


def _build_cautious_case() -> Dict[str, Any]:
    return build_system_brain_context(
        smi_posture_packet=_sample_smi_pattern_posture("cautious"),
        temporal_awareness_packet=_sample_temporal_awareness(),
        pattern_recognition_packet=_sample_pattern_recognition(),
        unified_awareness_packet=_sample_unified_awareness("stable"),
        cross_run_intelligence_packet=_sample_cross_run("volatile"),
    )


def _build_source_error_case() -> Dict[str, Any]:
    return build_system_brain_context(
        smi_posture_packet=_sample_smi_pattern_posture("pattern_observed"),
        temporal_awareness_packet={
            "status": "unavailable",
            "artifact_type": "temporal_awareness_packet",
            "error": "test_unavailable",
        },
        pattern_recognition_packet=_sample_pattern_recognition(),
        unified_awareness_packet=_sample_unified_awareness("stable"),
        cross_run_intelligence_packet=_sample_cross_run("stable"),
    )


def _assert_base_shape(packet: Dict[str, Any]) -> None:
    assert packet["status"] == "ok"
    assert packet["artifact_type"] == "system_brain_context"
    assert packet["artifact_version"] == "v1.0"
    assert packet["mode"] == "read_only"
    assert packet["sealed"] is True

    assert isinstance(packet["summary"], dict)
    assert isinstance(packet["operator_cards"], list)
    assert len(packet["operator_cards"]) >= 1
    assert isinstance(packet["what_to_watch"], list)
    assert len(packet["what_to_watch"]) >= 1

    assert "smi_pattern_posture" in packet["source_surfaces"]
    assert "temporal_awareness" in packet["source_surfaces"]
    assert "pattern_recognition" in packet["source_surfaces"]
    assert "unified_system_awareness" in packet["source_surfaces"]
    assert "cross_run_intelligence" in packet["source_surfaces"]

    _assert_no_authority(packet)


def run_probe() -> Dict[str, Any]:
    stable_case = _build_stable_case()
    cautious_case = _build_cautious_case()
    source_error_case = _build_source_error_case()

    _assert_base_shape(stable_case)
    _assert_base_shape(cautious_case)
    _assert_base_shape(source_error_case)

    assert stable_case["summary"]["risk_posture"] == "stable_observed"
    assert stable_case["summary"]["smi_posture"] == "pattern_observed"
    assert stable_case["summary"]["cross_run_drift"] == "stable"
    assert stable_case["summary"]["pattern_signal_count"] >= 6

    assert cautious_case["summary"]["risk_posture"] == "cautious"
    assert cautious_case["summary"]["smi_posture"] == "cautious"
    assert cautious_case["summary"]["cross_run_drift"] == "volatile"

    assert source_error_case["summary"]["risk_posture"] == "cautious"
    assert source_error_case["summary"]["source_error_count"] >= 1
    assert source_error_case["validation"]["source_error_count"] >= 1

    compact = summarize_system_brain_context(stable_case)
    assert compact["advisory_only"] is True
    assert compact["execution_allowed"] is False
    assert compact["mutation_allowed"] is False
    assert compact["risk_posture"] == "stable_observed"

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "stable_case": {
            "risk_posture": stable_case["summary"]["risk_posture"],
            "pattern_signal_count": stable_case["summary"]["pattern_signal_count"],
            "authority_valid": stable_case["validation"]["valid"],
        },
        "cautious_case": {
            "risk_posture": cautious_case["summary"]["risk_posture"],
            "cross_run_drift": cautious_case["summary"]["cross_run_drift"],
            "authority_valid": cautious_case["validation"]["valid"],
        },
        "source_error_case": {
            "risk_posture": source_error_case["summary"]["risk_posture"],
            "source_error_count": source_error_case["summary"]["source_error_count"],
            "authority_valid": source_error_case["validation"]["valid"],
        },
        "summary_contract": compact,
        "next": {
            "phase": "5D.4",
            "recommended_step": "Wire System Brain context into the operator System Brain surface and API without adding authority.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D3_SYSTEM_BRAIN_AGGREGATOR_PROBE: PASS")
    print(result)