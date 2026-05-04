from __future__ import annotations

from AI_GO.core.pm.pm_decision_conditioning import (
    build_pm_decision_conditioning_packet,
    summarize_pm_decision_conditioning,
)


def run_probe() -> dict:
    packet = build_pm_decision_conditioning_packet()
    summary = summarize_pm_decision_conditioning()

    assert packet["artifact_type"] == "pm_decision_conditioning_packet"
    assert packet["mode"] == "passive"
    assert packet["sealed"] is True

    assert packet["authority"]["pm_context_only"] is True
    assert packet["authority"]["advisory_only"] is True
    assert packet["authority"]["passive_only"] is True
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False
    assert packet["authority"]["can_override_governance"] is False
    assert packet["authority"]["can_override_watcher"] is False
    assert packet["authority"]["can_override_execution_gate"] is False
    assert packet["authority"]["can_write_decision"] is False
    assert packet["authority"]["can_auto_apply"] is False

    assert packet["use_policy"]["pm_may_read"] is True
    assert packet["use_policy"]["pm_may_reference_in_decision_notes"] is True
    assert packet["use_policy"]["may_change_execution_gate"] is False
    assert packet["use_policy"]["may_change_watcher"] is False
    assert packet["use_policy"]["may_change_state"] is False
    assert packet["use_policy"]["may_auto_create_decision"] is False
    assert packet["use_policy"]["may_auto_transition_workflow"] is False

    assert "conditioning" in packet
    assert "conditioned_risk_posture" in packet["conditioning"]
    assert "conditioned_review_depth" in packet["conditioning"]
    assert "escalation_hint" in packet["conditioning"]

    assert summary["status"] == "ok"
    assert summary["mode"] == "passive"

    return {
        "status": "passed",
        "phase": "Phase 4.6",
        "layer": "pm_decision_conditioning",
        "mode": packet["mode"],
        "recommended_posture": packet["conditioning"]["recommended_posture"],
        "conditioned_risk_posture": packet["conditioning"]["conditioned_risk_posture"],
        "conditioned_review_depth": packet["conditioning"]["conditioned_review_depth"],
        "escalation_hint": packet["conditioning"]["escalation_hint"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_PM_DECISION_CONDITIONING_PROBE: PASS")
    print(result)