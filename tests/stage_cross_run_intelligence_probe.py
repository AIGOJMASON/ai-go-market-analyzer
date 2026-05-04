from __future__ import annotations

from AI_GO.core.awareness.cross_run_intelligence import (
    append_unified_awareness_history_record,
    build_cross_run_intelligence_packet,
    summarize_cross_run_intelligence,
)


def run_probe() -> dict:
    append_unified_awareness_history_record(
        run_id="phase4-8-cross-run-001",
        limit=500,
    )
    append_unified_awareness_history_record(
        run_id="phase4-8-cross-run-002",
        limit=500,
    )
    append_unified_awareness_history_record(
        run_id="phase4-8-cross-run-003",
        limit=500,
    )

    packet = build_cross_run_intelligence_packet(limit=100)
    summary = summarize_cross_run_intelligence(limit=100)

    assert packet["artifact_type"] == "cross_run_intelligence_packet"
    assert packet["mode"] == "read_only_cross_run_stitching"
    assert packet["sealed"] is True

    assert packet["authority"]["read_only"] is True
    assert packet["authority"]["advisory_only"] is True
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_operational_state"] is False
    assert packet["authority"]["can_override_governance"] is False
    assert packet["authority"]["can_override_watcher"] is False
    assert packet["authority"]["can_override_execution_gate"] is False
    assert packet["authority"]["can_auto_escalate"] is False
    assert packet["authority"]["can_auto_condition_pm"] is False

    assert packet["use_policy"]["operator_may_read"] is True
    assert packet["use_policy"]["pm_may_read"] is True
    assert packet["use_policy"]["ai_may_read_later"] is True
    assert packet["use_policy"]["may_change_execution_gate"] is False
    assert packet["use_policy"]["may_change_watcher"] is False
    assert packet["use_policy"]["may_change_state"] is False
    assert packet["use_policy"]["may_write_decisions"] is False
    assert packet["use_policy"]["may_dispatch_actions"] is False

    assert packet["source"]["history_count"] >= 3
    assert "trajectory" in packet
    assert "drift_detection" in packet
    assert "persistence_detection" in packet
    assert "summary" in packet

    assert packet["trajectory"]["point_count"] >= 3
    assert summary["status"] == "ok"

    return {
        "status": "passed",
        "phase": "Phase 4.8",
        "layer": "cross_run_intelligence",
        "mode": packet["mode"],
        "cross_run_posture": packet["summary"]["cross_run_posture"],
        "history_count": packet["summary"]["history_count"],
        "drift": packet["summary"]["drift"],
        "persistent_signal_count": packet["summary"]["persistent_signal_count"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_CROSS_RUN_INTELLIGENCE_PROBE: PASS")
    print(result)