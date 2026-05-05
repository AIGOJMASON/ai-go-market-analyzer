# AI_GO/tests/stage_refinement_to_pm_bridge_probe.py

from __future__ import annotations

from core.refinement.refinement_to_pm_bridge import (
    generate_and_persist_pm_refinement_intake_record,
)


def run_probe():
    record = generate_and_persist_pm_refinement_intake_record()

    results = []

    results.append({
        "case": "case_01_record_generated",
        "status": "passed" if record.get("record_id") else "failed",
    })

    results.append({
        "case": "case_02_annotation_only_preserved",
        "status": "passed" if record.get("annotation_only") is True else "failed",
    })

    results.append({
        "case": "case_03_top_pattern_key_present",
        "status": "passed" if record.get("top_pattern_key") else "failed",
    })

    results.append({
        "case": "case_04_confidence_posture_present",
        "status": "passed" if record.get("confidence_posture") else "failed",
    })

    results.append({
        "case": "case_05_source_packet_path_present",
        "status": "passed" if record.get("source_packet_path") else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
        "record": record,
    }


if __name__ == "__main__":
    print(run_probe())