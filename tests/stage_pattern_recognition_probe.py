from __future__ import annotations

from AI_GO.core.awareness.pattern_recognition import build_pattern_recognition_packet


def run_probe():
    packet = build_pattern_recognition_packet()

    assert packet["artifact_type"] == "pattern_recognition_packet"

    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False
    assert packet["authority"]["can_influence_execution"] is False

    assert "patterns" in packet
    assert "pattern_signals" in packet

    assert isinstance(packet["patterns"]["action_patterns"], list)
    assert isinstance(packet["patterns"]["failure_patterns"], list)
    assert isinstance(packet["patterns"]["project_patterns"], list)

    return {
        "status": "passed",
        "phase": "Phase 4.4",
        "layer": "pattern_recognition",
        "pattern_count": packet["summary"]["pattern_count"],
        "signal_count": packet["summary"]["signal_count"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_PATTERN_RECOGNITION_PROBE: PASS")
    print(result)