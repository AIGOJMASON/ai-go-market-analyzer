# AI_GO/tests/stage_continuity_weighting_refinement_bridge_probe.py

from __future__ import annotations

from core.refinement.continuity_weighting_bridge import (
    generate_and_persist_continuity_weighting_refinement_packet,
)


def run_probe():
    packet = generate_and_persist_continuity_weighting_refinement_packet()

    results = []

    results.append({
        "case": "case_01_packet_generated",
        "status": "passed" if packet.get("packet_id") else "failed",
    })

    results.append({
        "case": "case_02_annotation_only_true",
        "status": "passed" if packet.get("annotation_only") is True else "failed",
    })

    results.append({
        "case": "case_03_top_pattern_key_present",
        "status": "passed" if packet.get("top_pattern_key") else "failed",
    })

    results.append({
        "case": "case_04_confidence_posture_present",
        "status": "passed" if packet.get("confidence_posture") else "failed",
    })

    results.append({
        "case": "case_05_advisory_note_present",
        "status": "passed" if packet.get("advisory_note") else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
        "packet": packet,
    }


if __name__ == "__main__":
    print(run_probe())