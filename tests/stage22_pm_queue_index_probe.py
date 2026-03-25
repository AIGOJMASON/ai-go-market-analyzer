from AI_GO.core.pm_continuity.pm_continuity_index import update_pm_continuity_index
from AI_GO.core.pm_continuity.pm_continuity_record import build_pm_continuity_record
from AI_GO.core.strategy.pm_planning_record import build_pm_planning_record
from AI_GO.core.strategy.pm_queue_index import build_pm_queue_index
from AI_GO.core.strategy.pm_queue_record import build_pm_queue_record
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


def _build_queue(
    queue_id: str,
    strategy_id: str,
    review_id: str,
    planning_id: str,
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
    review = build_pm_review_record(strategy, review_id)
    planning = build_pm_planning_record(review, planning_id)
    return build_pm_queue_record(planning, queue_id)


def run_probe() -> dict:
    results = []

    def record_result(case_name: str, status: str, error: str | None = None) -> None:
        entry = {"case": case_name, "status": status}
        if error is not None:
            entry["error"] = error
        results.append(entry)

    queue_records = [
        _build_queue(
            queue_id="pmqueue_001",
            strategy_id="pmstrat_001",
            review_id="pmrev_001",
            planning_id="pmplan_001",
            record_id="pmrec_001",
            index_id="pmidx_001",
            case_id="case_001",
            repeats=1,
        ),
        _build_queue(
            queue_id="pmqueue_002",
            strategy_id="pmstrat_002",
            review_id="pmrev_002",
            planning_id="pmplan_002",
            record_id="pmrec_002",
            index_id="pmidx_002",
            case_id="case_002",
            repeats=2,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=3,
        ),
        _build_queue(
            queue_id="pmqueue_003",
            strategy_id="pmstrat_003",
            review_id="pmrev_003",
            planning_id="pmplan_003",
            record_id="pmrec_003",
            index_id="pmidx_003",
            case_id="case_003",
            repeats=2,
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
        ),
        _build_queue(
            queue_id="pmqueue_004",
            strategy_id="pmstrat_004",
            review_id="pmrev_004",
            planning_id="pmplan_004",
            record_id="pmrec_004",
            index_id="pmidx_004",
            case_id="case_004",
            repeats=4,
            arbitration_class="cautionary",
            confidence_adjustment="down",
            accepted_matches=1,
            quarantined_matches=4,
        ),
    ]

    # case_01_valid_index_construction
    try:
        index_payload = build_pm_queue_index(
            pm_queue_records=queue_records,
            index_id="pmqidx_001",
        )
        assert index_payload["artifact_type"] == "pm_queue_index"
        assert index_payload["sealed"] is True
        assert index_payload["entry_count"] == 4
        record_result("case_01_valid_index_construction", "passed")
    except Exception as exc:
        record_result("case_01_valid_index_construction", "failed", str(exc))

    # case_02_reject_unsealed_queue_record
    try:
        bad_records = list(queue_records)
        bad_record = dict(bad_records[0])
        bad_record["sealed"] = False
        bad_records[0] = bad_record
        build_pm_queue_index(
            pm_queue_records=bad_records,
            index_id="pmqidx_002",
        )
        record_result("case_02_reject_unsealed_queue_record", "failed", "expected rejection")
    except Exception:
        record_result("case_02_reject_unsealed_queue_record", "passed")

    # case_03_filter_by_queue_lane
    try:
        index_payload = build_pm_queue_index(
            pm_queue_records=queue_records,
            index_id="pmqidx_003",
            filters={"queue_lane": "pm_review_queue"},
        )
        assert index_payload["entry_count"] == 1
        assert index_payload["entries"][0]["queue_lane"] == "pm_review_queue"
        record_result("case_03_filter_by_queue_lane", "passed")
    except Exception as exc:
        record_result("case_03_filter_by_queue_lane", "failed", str(exc))

    # case_04_filter_by_queue_status
    try:
        index_payload = build_pm_queue_index(
            pm_queue_records=queue_records,
            index_id="pmqidx_004",
            filters={"queue_status": "queued"},
        )
        assert index_payload["entry_count"] == 3
        for entry in index_payload["entries"]:
            assert entry["queue_status"] == "queued"
        record_result("case_04_filter_by_queue_status", "passed")
    except Exception as exc:
        record_result("case_04_filter_by_queue_status", "failed", str(exc))

    # case_05_filter_by_queue_target_and_limit
    try:
        index_payload = build_pm_queue_index(
            pm_queue_records=queue_records,
            index_id="pmqidx_005",
            filters={"queue_target": "planning"},
            limit=1,
        )
        assert index_payload["entry_count"] == 1
        assert index_payload["entries"][0]["queue_target"] == "planning"
        record_result("case_05_filter_by_queue_target_and_limit", "passed")
    except Exception as exc:
        record_result("case_05_filter_by_queue_target_and_limit", "failed", str(exc))

    # case_06_invalid_filter_rejected
    try:
        build_pm_queue_index(
            pm_queue_records=queue_records,
            index_id="pmqidx_006",
            filters={"bad_field": "x"},
        )
        record_result("case_06_invalid_filter_rejected", "failed", "expected rejection")
    except Exception:
        record_result("case_06_invalid_filter_rejected", "passed")

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())