from __future__ import annotations

from AI_GO.core.awareness.posture_explanation import build_posture_explanation_packet


def run_probe() -> dict:
    packet = build_posture_explanation_packet()

    assert packet["artifact_type"] == "posture_explanation_packet"
    assert packet["mode"] == "deterministic_read_only_explanation"
    assert packet["sealed"] is True

    assert packet["authority"]["read_only"] is True
    assert packet["authority"]["advisory_only"] is True
    assert packet["authority"]["deterministic"] is True
    assert packet["authority"]["ai_generated"] is False
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False
    assert packet["authority"]["can_override_governance"] is False
    assert packet["authority"]["can_override_watcher"] is False
    assert packet["authority"]["can_override_execution_gate"] is False
    assert packet["authority"]["can_create_decision"] is False
    assert packet["authority"]["can_escalate_automatically"] is False

    assert packet["use_policy"]["operator_may_read"] is True
    assert packet["use_policy"]["may_display_in_dashboard"] is True
    assert packet["use_policy"]["may_change_execution_gate"] is False
    assert packet["use_policy"]["may_change_watcher"] is False
    assert packet["use_policy"]["may_change_state"] is False
    assert packet["use_policy"]["may_write_decisions"] is False
    assert packet["use_policy"]["may_dispatch_actions"] is False

    assert "plain_explanation" in packet["summary"]
    assert isinstance(packet["summary"]["plain_explanation"], str)
    assert len(packet["summary"]["plain_explanation"]) > 0
    assert isinstance(packet["reasons"], list)

    return {
        "status": "passed",
        "phase": "Phase 4.12.1",
        "layer": "posture_explanation",
        "system_posture": packet["summary"]["system_posture"],
        "conditioned_risk_posture": packet["summary"]["conditioned_risk_posture"],
        "reason_count": packet["summary"]["reason_count"],
        "plain_explanation": packet["summary"]["plain_explanation"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_POSTURE_EXPLANATION_PROBE: PASS")
    print(result)