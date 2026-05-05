from __future__ import annotations

from AI_GO.core.pm.pm_pattern_influence import build_pm_pattern_influence_packet


def run_probe():
    packet = build_pm_pattern_influence_packet()

    assert packet["artifact_type"] == "pm_pattern_influence_packet"

    assert packet["authority"]["pm_only"] is True
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False
    assert packet["authority"]["can_override_governance"] is False

    assert "pattern_influence" in packet

    influence = packet["pattern_influence"]

    assert "recommended_posture" in packet["summary"]
    assert isinstance(influence["influences"], list)

    return {
        "status": "passed",
        "phase": "Phase 4.5",
        "layer": "pm_pattern_influence",
        "recommended_posture": packet["summary"]["recommended_posture"],
        "risk_score": packet["summary"]["risk_score"],
        "confidence_score": packet["summary"]["confidence_score"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_PM_PATTERN_INFLUENCE_PROBE: PASS")
    print(result)