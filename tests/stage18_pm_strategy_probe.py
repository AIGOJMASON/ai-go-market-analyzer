from AI_GO.core.pm_continuity.pm_continuity_index import update_pm_continuity_index
from AI_GO.core.pm_continuity.pm_continuity_record import build_pm_continuity_record
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


def _build_record(case_id: str, record_id: str, **kwargs) -> dict:
    refinement_packet = _make_refinement_packet(case_id=case_id, **kwargs)
    return build_pm_continuity_record(
        refinement_packet=refinement_packet,
        record_id=record_id,
    )


def run_probe() -> dict:
    results: list[dict] = []

    def record_result(case_name: str, status: str, error: str | None = None) -> None:
        entry = {"case": case_name, "status": status}
        if error is not None:
            entry["error"] = error
        results.append(entry)

    # case_01_valid_strategy_construction
    try:
        record = _build_record("case_001", "pmrec_001")
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record,
            index_id="pmidx_001",
            existing_index=None,
        )
        strategy = build_pm_strategy_record(
            pm_continuity_record=record,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_001",
        )
        assert strategy["artifact_type"] == "pm_strategy_record"
        assert strategy["sealed"] is True
        assert strategy["memory_only"] is True
        assert strategy["runtime_mutation_allowed"] is False
        assert strategy["execution_influence"] is False
        assert strategy["recommendation_mutation_allowed"] is False
        record_result("case_01_valid_strategy_construction", "passed")
    except Exception as exc:
        record_result("case_01_valid_strategy_construction", "failed", str(exc))

    # case_02_reject_unsealed_continuity_record
    try:
        record = _build_record("case_002", "pmrec_002")
        record["sealed"] = False
        index_payload = update_pm_continuity_index(
            pm_continuity_record=_build_record("case_002_idx", "pmrec_002_idx"),
            index_id="pmidx_002",
            existing_index=None,
        )
        build_pm_strategy_record(
            pm_continuity_record=record,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_002",
        )
        record_result("case_02_reject_unsealed_continuity_record", "failed", "expected rejection")
    except Exception:
        record_result("case_02_reject_unsealed_continuity_record", "passed")

    # case_03_insufficient_pattern_on_single_count
    try:
        record = _build_record("case_003", "pmrec_003")
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record,
            index_id="pmidx_003",
            existing_index=None,
        )
        strategy = build_pm_strategy_record(
            pm_continuity_record=record,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_003",
        )
        assert strategy["strategy_class"] == "insufficient_pattern"
        record_result("case_03_insufficient_pattern_on_single_count", "passed")
    except Exception as exc:
        record_result("case_03_insufficient_pattern_on_single_count", "failed", str(exc))

    # case_04_elevated_caution_on_repeated_cautionary_continuity
    try:
        record_a = _build_record("case_004_a", "pmrec_004_a")
        record_b = _build_record("case_004_b", "pmrec_004_b")
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_a,
            index_id="pmidx_004",
            existing_index=None,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_b,
            index_id="pmidx_004",
            existing_index=index_payload,
        )
        strategy = build_pm_strategy_record(
            pm_continuity_record=record_b,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_004",
        )
        assert strategy["strategy_class"] == "elevated_caution"
        record_result("case_04_elevated_caution_on_repeated_cautionary_continuity", "passed")
    except Exception as exc:
        record_result("case_04_elevated_caution_on_repeated_cautionary_continuity", "failed", str(exc))

    # case_05_reinforced_support_on_repeated_supportive_continuity
    try:
        record_a = _build_record(
            "case_005_a",
            "pmrec_005_a",
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
            analog_matches=2,
        )
        record_b = _build_record(
            "case_005_b",
            "pmrec_005_b",
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
            analog_matches=2,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_a,
            index_id="pmidx_005",
            existing_index=None,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_b,
            index_id="pmidx_005",
            existing_index=index_payload,
        )
        strategy = build_pm_strategy_record(
            pm_continuity_record=record_b,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_005",
        )
        assert strategy["strategy_class"] == "reinforced_support"
        record_result("case_05_reinforced_support_on_repeated_supportive_continuity", "passed")
    except Exception as exc:
        record_result("case_05_reinforced_support_on_repeated_supportive_continuity", "failed", str(exc))

    # case_06_monitor_on_branching_continuity
    try:
        record_a = _build_record(
            "case_006_a",
            "pmrec_006_a",
            signal_class="supply_expansion_partial_confirmation",
            arbitration_class="cautionary",
            confidence_adjustment="down",
        )
        record_b = _build_record(
            "case_006_b",
            "pmrec_006_b",
            signal_class="supply_expansion_partial_confirmation",
            arbitration_class="supportive",
            confidence_adjustment="up",
            accepted_matches=3,
            quarantined_matches=0,
            analog_matches=1,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_a,
            index_id="pmidx_006",
            existing_index=None,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record_b,
            index_id="pmidx_006",
            existing_index=index_payload,
        )
        strategy = build_pm_strategy_record(
            pm_continuity_record=record_a,
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_006",
        )
        assert strategy["strategy_class"] == "monitor"
        record_result("case_06_monitor_on_branching_continuity", "passed")
    except Exception as exc:
        record_result("case_06_monitor_on_branching_continuity", "failed", str(exc))

    # case_07_escalate_for_pm_review_on_high_strength_cautionary_continuity
    try:
        records = [
            _build_record(
                f"case_007_{idx}",
                f"pmrec_007_{idx}",
                arbitration_class="cautionary",
                confidence_adjustment="down",
                accepted_matches=1,
                quarantined_matches=4,
                analog_matches=2,
            )
            for idx in range(4)
        ]
        index_payload = None
        for record in records:
            index_payload = update_pm_continuity_index(
                pm_continuity_record=record,
                index_id="pmidx_007",
                existing_index=index_payload,
            )
        strategy = build_pm_strategy_record(
            pm_continuity_record=records[-1],
            pm_continuity_index=index_payload,
            strategy_id="pmstrat_007",
        )
        assert strategy["strategy_class"] == "escalate_for_pm_review"
        record_result("case_07_escalate_for_pm_review_on_high_strength_cautionary_continuity", "passed")
    except Exception as exc:
        record_result("case_07_escalate_for_pm_review_on_high_strength_cautionary_continuity", "failed", str(exc))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())