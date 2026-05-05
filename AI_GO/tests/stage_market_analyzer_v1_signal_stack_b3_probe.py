from __future__ import annotations

try:
    from api.signal_stack import build_signal_stack
except ModuleNotFoundError:
    from AI_GO.api.signal_stack import build_signal_stack


def run_probe():
    results = []

    classification = {
        "artifact_type": "event_classification",
        "request_id": "stack-001",
        "event_theme": "supply_expansion",
        "classification_confidence": "high",
        "signals": ["keyword:chile", "keyword:copper", "sector:lawful_exception"],
        "bounded": True,
        "sealed": True,
    }

    stack = build_signal_stack(
        request_id="stack-001",
        symbol="COPX",
        headline="New Chile copper mine opening expands future supply outlook",
        price_change_pct=1.1,
        sector="materials",
        confirmation="partial",
        classification=classification,
    )

    results.append(
        {
            "case": "case_01_signal_stack_artifact_created",
            "status": "passed"
            if stack["artifact_type"] == "signal_stack_record"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_classifier_signals_preserved",
            "status": "passed"
            if "keyword:chile" in stack["stack_signals"]
            and "sector:lawful_exception" in stack["stack_signals"]
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_03_derived_signals_added",
            "status": "passed"
            if "confirmation:partial" in stack["stack_signals"]
            and "price:positive" in stack["stack_signals"]
            and "price_magnitude:medium" in stack["stack_signals"]
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_04_legality_summary_matches_lawful_exception",
            "status": "passed"
            if stack["stack_summary"]["legality_state"] == "lawful_exception"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_05_signal_stack_bounded_and_sealed",
            "status": "passed"
            if stack["bounded"] is True and stack["sealed"] is True
            else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())