from AI_GO.core.runtime.refinement.refinement_arbitrator import (
    build_refinement_arbitrator_packet_from_runtime,
)


def run_probe():
    result = build_refinement_arbitrator_packet_from_runtime(
        core_id="market_analyzer_v1",
        market_panel={
            "event_theme": "supply_expansion",
            "historical_analog_confidence": "high",
            "historical_analog_count": 2,
        },
        historical_analog_panel={
            "analog_count": 2,
            "common_pattern": "Delayed price impact after initial enthusiasm.",
            "failure_mode": "Early reversal before confirmation strengthens.",
            "confidence_band": "high",
        },
        governance_panel={
            "watcher_passed": True,
            "approval_required": True,
            "execution_allowed": False,
        },
        quarantine_items=[],
    )

    results = []

    results.append({
        "case": "case_01_artifact_type",
        "status": "passed" if result["artifact_type"] == "refinement_arbitrator_packet" else "failed",
    })
    results.append({
        "case": "case_02_sealed",
        "status": "passed" if result["sealed"] is True else "failed",
    })
    results.append({
        "case": "case_03_core_id",
        "status": "passed" if result["core_id"] == "market_analyzer_v1" else "failed",
    })
    results.append({
        "case": "case_04_confidence_adjustment_valid",
        "status": "passed" if result["confidence_adjustment"] in {"up", "down", "none"} else "failed",
    })
    results.append({
        "case": "case_05_refinement_mode_valid",
        "status": "passed" if result["refinement_mode"] in {"annotation_only", "confidence_conditioning"} else "failed",
    })
    results.append({
        "case": "case_06_reasoning_present",
        "status": "passed" if bool(result["reasoning_summary"]) else "failed",
    })
    results.append({
        "case": "case_07_narrative_present",
        "status": "passed" if bool(result["narrative_summary"]) else "failed",
    })
    results.append({
        "case": "case_08_risk_flags_present",
        "status": "passed" if isinstance(result["risk_flags"], list) and len(result["risk_flags"]) > 0 else "failed",
    })
    results.append({
        "case": "case_09_source_lineage_present",
        "status": "passed" if isinstance(result["source_lineage"], dict) else "failed",
    })
    results.append({
        "case": "case_10_no_mutation_signal",
        "status": "passed" if "No recommendation mutation occurred." in result["notes"] else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())