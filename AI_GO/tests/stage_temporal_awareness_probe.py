from __future__ import annotations

from AI_GO.core.awareness.temporal_awareness import build_temporal_awareness_packet


def run_probe():
    packet = build_temporal_awareness_packet()

    assert packet["artifact_type"] == "temporal_awareness_packet"
    assert packet["authority"]["can_execute"] is False
    assert packet["authority"]["can_mutate_state"] is False

    assert "temporal_sequences" in packet
    assert "temporal_signals" in packet

    assert isinstance(packet["temporal_sequences"], list)
    assert isinstance(packet["temporal_signals"], dict)

    return {
        "status": "passed",
        "phase": "Phase 4.3",
        "layer": "temporal_awareness",
        "sequence_count": packet["summary"]["sequence_count"],
        "dominant_pattern": packet["summary"]["dominant_pattern"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_TEMPORAL_AWARENESS_PROBE: PASS")
    print(result)