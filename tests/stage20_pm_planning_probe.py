from AI_GO.core.pm_continuity.pm_continuity_index import update_pm_continuity_index
from AI_GO.core.pm_continuity.pm_continuity_record import build_pm_continuity_record
from AI_GO.core.strategy.pm_planning_record import build_pm_planning_record
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


def _build_review(
    strategy_id: str,
    review_id: str,
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

    strategy = build_pm_strategy_record(
        pm_continuity_record=last_record,
        pm_continuity_index=index_payload,
        strategy_id=strategy_id,
    )
    return build_pm_review_record(strategy, review_id)


def run_probe() -> dict:
    results = []

    def record_result(case_name: str, status: str, error: str | None = None) -> None:
        entry = {"case": case_name, "status": status}
        if error is not None:
            entry["error"] = error
        results.append(entry)

    # case_01_valid_planning_construction
    try:
        review = _build_review(
            strategy_id="pmstrat_001",
            review_id="pmrev_001",
            record_id="pmrec_001",
            index_id="pmidx_001",
            case_id="case_001",
            repeats=2,
        )
        planning = build_pm_planning_record(review, "pmplan_001")
        assert planning["artifact_type"] == "pm_planning_record"
        assert planning["sealed"] is True
        assert planning["memory_only"] is True
        assert planning["runtime_mutation_allowed"] is False
        assert planning["execution_influence"] is False
        assert planning["recommendation_mutation_allowed"] is False
        record_result("case_01_valid_planning_construction", "passed")
    except Exception as exc:
        record_result("case_01_valid_planning_construction", "failed", str(exc))

    # case_02_reject_unsealed_review_record
    try:
        review = _build_review(
            strategy_id="pmstrat_002",
            review_id="pmrev_002",
            record_id="pmrec_002",
            index_id="pmidx_002",
            case_id="case_002",
            repeats=2,
        )
        review["sealed"] = False
        build_pm_planning_record(review, "pmplan_002")
        record_result("case_02_reject_unsealed_review_record", "failed", "expected rejection")
    except Exception:
        record_result("case_02_reject_unsealed_review_record", "passed")

    # case_03_hold_observe_on_observe_review
    try:
        review = _build_review(
            strategy_id="pmstrat_003",
            review_id="pmrev_003",
            record_id="pmrec_003",
            index_id="pmidx_003",
            case_id="case_003",
            repeats=1,
        )
        planning = build_pm_planning_record(review, "pmplan_003")
        assert planning["plan_class"] == "hold_observe"
        assert planning["next_step_class"] == "no_action"
        record_result("case_03_hold_observe_on_observe_review", "passed")
    except Exception as exc:
        record_result("case_03_hold_observe_on_observe_review", "failed", str(exc))

    # case_04_prepare_review_on_review_class
    try:
        review = _build_review(
            strategy_id="pmstrat_004",
            review_id="pmrev_004",
            record_id="pmrec_004",
            index_id="pmidx_004",
            case_id="case_004",
            repeats=2,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=3,
        )
        planning = build_pm_planning_record(review, "pmplan_004")
        assert planning["plan_class"] == "prepare_review"
        assert planning["next_step_class"] == "queue_for_pm_review"
        record_result("case_04_prepare_review_on_review_class", "passed")
    except Exception as exc:
        record_result("case_04_prepare_review_on_review_class", "failed", str(exc))

    # case_05_prepare_plan_on_plan_class
    try:
        review = _build_review(
            strategy_id="pmstrat_005",
            review_id="pmrev_005",
            record_id="pmrec_005",
            index_id="pmidx_005",
            case_id="case_005",
            repeats=2,
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
        )
        planning = build_pm_planning_record(review, "pmplan_005")
        assert planning["plan_class"] == "prepare_plan"
        assert planning["next_step_class"] == "queue_for_pm_planning"
        record_result("case_05_prepare_plan_on_plan_class", "passed")
    except Exception as exc:
        record_result("case_05_prepare_plan_on_plan_class", "failed", str(exc))

    # case_06_prepare_escalation_on_escalate_class
    try:
        review = _build_review(
            strategy_id="pmstrat_006",
            review_id="pmrev_006",
            record_id="pmrec_006",
            index_id="pmidx_006",
            case_id="case_006",
            repeats=4,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=4,
        )
        planning = build_pm_planning_record(review, "pmplan_006")
        assert planning["plan_class"] == "prepare_escalation"
        assert planning["next_step_class"] == "queue_for_pm_escalation"
        record_result("case_06_prepare_escalation_on_escalate_class", "passed")
    except Exception as exc:
        record_result("case_06_prepare_escalation_on_escalate_class", "failed", str(exc))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())