# AI_GO/tests/stage_continuity_weighting_probe.py

from __future__ import annotations

from core.continuity_weighting.continuity_weighting_record import generate_and_persist_continuity_weighting_record


def run_probe():
    record = generate_and_persist_continuity_weighting_record()

    ranked_patterns = record.get("ranked_patterns", [])
    summary = record.get("summary", {})

    results = []

    results.append({
        "case": "case_01_record_generated",
        "status": "passed" if record.get("record_id") else "failed",
    })

    results.append({
        "case": "case_02_ranked_patterns_present",
        "status": "passed" if isinstance(ranked_patterns, list) else "failed",
    })

    if ranked_patterns:
        top = ranked_patterns[0]
        results.append({
            "case": "case_03_top_pattern_has_weight",
            "status": "passed" if top.get("weight") is not None else "failed",
        })
        results.append({
            "case": "case_04_top_pattern_has_status",
            "status": "passed" if top.get("pattern_status") else "failed",
        })
        results.append({
            "case": "case_05_summary_matches_top_pattern",
            "status": "passed" if summary.get("top_pattern_key") == top.get("continuity_key") else "failed",
        })
    else:
        results.append({
            "case": "case_03_top_pattern_has_weight",
            "status": "failed",
        })
        results.append({
            "case": "case_04_top_pattern_has_status",
            "status": "failed",
        })
        results.append({
            "case": "case_05_summary_matches_top_pattern",
            "status": "failed",
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