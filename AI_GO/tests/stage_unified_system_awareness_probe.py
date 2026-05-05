from __future__ import annotations

from AI_GO.core.awareness.unified_system_awareness import (
    build_unified_system_awareness_packet,
    summarize_unified_system_awareness,
)


def run_probe() -> dict:
    packet = build_unified_system_awareness_packet()
    summary = summarize_unified_system_awareness()

    assert packet["artifact_type"] == "unified_system_awareness_packet"
    assert packet["mode"] == "read_only_system_brain_view"
    assert packet["sealed"] is True

    assert packet["authority"]["read_only"] is True
    assert packet["authority"]["advisory_only"] is True
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False
    assert packet["authority"]["can_override_governance"] is False
    assert packet["authority"]["can_override_watcher"] is False
    assert packet["authority"]["can_override_execution_gate"] is False
    assert packet["authority"]["can_auto_create_decision"] is False
    assert packet["authority"]["can_auto_apply_conditioning"] is False

    assert packet["use_policy"]["operator_may_read"] is True
    assert packet["use_policy"]["pm_may_read"] is True
    assert packet["use_policy"]["ai_may_read_later"] is True
    assert packet["use_policy"]["may_change_execution_gate"] is False
    assert packet["use_policy"]["may_change_watcher"] is False
    assert packet["use_policy"]["may_change_state"] is False
    assert packet["use_policy"]["may_write_decisions"] is False
    assert packet["use_policy"]["may_dispatch_actions"] is False

    assert "governance_awareness" in packet["surfaces"]
    assert "memory_index" in packet["surfaces"]
    assert "temporal_awareness" in packet["surfaces"]
    assert "pattern_recognition" in packet["surfaces"]
    assert "pm_pattern_influence" in packet["surfaces"]
    assert "pm_decision_conditioning" in packet["surfaces"]

    assert summary["status"] == "ok"
    assert summary["mode"] == "read_only_system_brain_view"

    return {
        "status": "passed",
        "phase": "Phase 4.7",
        "layer": "unified_system_awareness",
        "mode": packet["mode"],
        "system_posture": packet["summary"]["system_posture"],
        "conditioned_risk_posture": packet["summary"]["conditioned_risk_posture"],
        "anomaly_count": packet["summary"]["anomaly_count"],
        "memory_record_count": packet["summary"]["memory_record_count"],
        "sequence_count": packet["summary"]["sequence_count"],
        "pattern_signal_count": packet["summary"]["pattern_signal_count"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_UNIFIED_SYSTEM_AWARENESS_PROBE: PASS")
    print(result)