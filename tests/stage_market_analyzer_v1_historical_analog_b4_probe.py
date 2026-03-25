from AI_GO.api.historical_analog import build_historical_analog_record


def run_probe():
    classification_panel = {
        "event_theme": "supply_expansion",
        "classification_confidence": "medium",
        "signals": [
            "keyword:chile",
            "keyword:copper",
            "sector:materials",
            "confirmation:partial",
            "price:positive",
            "price_magnitude:medium",
        ],
    }

    signal_stack_record = {
        "artifact_type": "signal_stack_record",
        "sealed": True,
        "stack_signals": [
            "keyword:chile",
            "keyword:copper",
            "sector:materials",
            "confirmation:partial",
            "price:positive",
            "price_magnitude:medium",
            "legality:lawful_exception",
        ],
        "stack_summary": {
            "price_direction": "positive",
            "confirmation_state": "partial",
            "legality_state": "lawful_exception",
            "signal_count": 7,
        },
    }

    record = build_historical_analog_record(
        classification_panel=classification_panel,
        signal_stack_record=signal_stack_record,
    )

    results = []

    results.append({
        "case": "case_01_artifact_type_valid",
        "status": "passed" if record["artifact_type"] == "historical_analog_record" else "failed",
    })
    results.append({
        "case": "case_02_record_is_sealed",
        "status": "passed" if record["sealed"] is True else "failed",
    })
    results.append({
        "case": "case_03_event_theme_preserved",
        "status": "passed" if record["event_theme"] == "supply_expansion" else "failed",
    })
    results.append({
        "case": "case_04_analog_count_positive",
        "status": "passed" if record["analog_count"] > 0 else "failed",
    })
    results.append({
        "case": "case_05_common_pattern_present",
        "status": "passed" if bool(record["common_pattern"]) else "failed",
    })
    results.append({
        "case": "case_06_failure_mode_present",
        "status": "passed" if bool(record["failure_mode"]) else "failed",
    })
    results.append({
        "case": "case_07_confidence_band_valid",
        "status": "passed" if record["confidence_band"] in {"low", "medium", "high"} else "failed",
    })
    results.append({
        "case": "case_08_selected_analogs_bounded",
        "status": "passed" if len(record["analogs"]) <= 3 else "failed",
    })
    results.append({
        "case": "case_09_notes_present",
        "status": "passed" if "No prediction" in record["notes"] else "failed",
    })
    results.append({
        "case": "case_10_source_lineage_present",
        "status": "passed" if record["source_lineage"]["signal_stack_artifact"] == "signal_stack_record" else "failed",
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