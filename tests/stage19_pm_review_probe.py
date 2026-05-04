from AI_GO.core.pm_continuity.pm_continuity_index import update_pm_continuity_index
from AI_GO.core.pm_continuity.pm_continuity_record import build_pm_continuity_record
from AI_GO.core.strategy.pm_review_record import build_pm_review_record
from AI_GO.core.strategy.pm_strategy_record import build_pm_strategy_record


def _make_refinement_packet(
    case_id: str,
    signal_class: str = "supply_expansion_partial_confirmation",
    arbitration_class: str = "cautionary",
    confidence_adjustment: str = "down",
    accepted_matches: int = 1,
    quarantined_matches: int = 3,
    analog_matches: int = 2,
) -> dict:
    return {
        "artifact_type": "refinement_packet",
        "artifact_version": "v1",
        "sealed": True,
        "case_id": case_id,
        "core_id": "market_analyzer_v1",
        "signal_class": signal_class,
        "arbitration_class": arbitration_class,
        "confidence_adjustment": confidence_adjustment,
        "risk_flags": ["early_reversal_likelihood"],
        "source_summary": {
            "accepted_matches": accepted_matches,
            "quarantined_matches": quarantined_matches,
            "analog_matches": analog_matches,
        },
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }


def _build_strategy(
    strategy_id: str,
    record_id: str,
    index_id: str,
    case_id: str,
    repeats: int = 1,
    **kwargs,
) -> dict:
    index_payload = None
    last_record = None
    for idx in range(repeats):
        refinement_packet = _make_refinement_packet(case_id=f"{case_id}_{idx}", **kwargs)
        last_record = build_pm_continuity_record(
            refinement_packet=refinement_packet,
            record_id=f"{record_id}_{idx}",
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=last_record,
            index_id=index_id,
            existing_index=index_payload,
        )

    return build_pm_strategy_record(
        pm_continuity_record=last_record,
        pm_continuity_index=index_payload,
        strategy_id=strategy_id,
    )


def run_probe() -> dict:
    results = []

    def record_result(case_name: str, status: str, error: str | None = None) -> None:
        entry = {"case": case_name, "status": status}
        if error is not None:
            entry["error"] = error
        results.append(entry)

    # case_01_valid_review_construction
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_001",
            record_id="pmrec_001",
            index_id="pmidx_001",
            case_id="case_001",
            repeats=2,
        )
        review = build_pm_review_record(strategy, "pmrev_001")
        assert review["artifact_type"] == "pm_review_record"
        assert review["sealed"] is True
        assert review["memory_only"] is True
        assert review["runtime_mutation_allowed"] is False
        assert review["execution_influence"] is False
        assert review["recommendation_mutation_allowed"] is False
        record_result("case_01_valid_review_construction", "passed")
    except Exception as exc:
        record_result("case_01_valid_review_construction", "failed", str(exc))

    # case_02_reject_unsealed_strategy_record
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_002",
            record_id="pmrec_002",
            index_id="pmidx_002",
            case_id="case_002",
            repeats=2,
        )
        strategy["sealed"] = False
        build_pm_review_record(strategy, "pmrev_002")
        record_result("case_02_reject_unsealed_strategy_record", "failed", "expected rejection")
    except Exception:
        record_result("case_02_reject_unsealed_strategy_record", "passed")

    # case_03_observe_on_insufficient_pattern
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_003",
            record_id="pmrec_003",
            index_id="pmidx_003",
            case_id="case_003",
            repeats=1,
        )
        review = build_pm_review_record(strategy, "pmrev_003")
        assert review["review_class"] == "observe"
        assert review["review_priority"] == "low"
        record_result("case_03_observe_on_insufficient_pattern", "passed")
    except Exception as exc:
        record_result("case_03_observe_on_insufficient_pattern", "failed", str(exc))

    # case_04_review_on_elevated_caution
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_004",
            record_id="pmrec_004",
            index_id="pmidx_004",
            case_id="case_004",
            repeats=2,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=3,
        )
        review = build_pm_review_record(strategy, "pmrev_004")
        assert review["review_class"] == "review"
        assert review["review_priority"] in {"medium", "high"}
        record_result("case_04_review_on_elevated_caution", "passed")
    except Exception as exc:
        record_result("case_04_review_on_elevated_caution", "failed", str(exc))

    # case_05_plan_on_reinforced_support
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_005",
            record_id="pmrec_005",
            index_id="pmidx_005",
            case_id="case_005",
            repeats=2,
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
        )
        review = build_pm_review_record(strategy, "pmrev_005")
        assert review["review_class"] == "plan"
        assert review["review_priority"] == "medium"
        record_result("case_05_plan_on_reinforced_support", "passed")
    except Exception as exc:
        record_result("case_05_plan_on_reinforced_support", "failed", str(exc))

    # case_06_escalate_on_pm_review_escalation
    try:
        strategy = _build_strategy(
            strategy_id="pmstrat_006",
            record_id="pmrec_006",
            index_id="pmidx_006",
            case_id="case_006",
            repeats=4,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=4,
        )
        review = build_pm_review_record(strategy, "pmrev_006")
        assert review["review_class"] == "escalate"
        assert review["review_priority"] == "high"
        record_result("case_06_escalate_on_pm_review_escalation", "passed")
    except Exception as exc:
        record_result("case_06_escalate_on_pm_review_escalation", "failed", str(exc))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())