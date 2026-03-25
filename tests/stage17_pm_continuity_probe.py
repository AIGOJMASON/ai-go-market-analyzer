from AI_GO.core.pm_continuity.pm_continuity_index import update_pm_continuity_index
from AI_GO.core.pm_continuity.pm_continuity_record import build_pm_continuity_record


def _make_refinement_packet(
    case_id: str,
    signal_class: str = "supply_expansion_partial_confirmation",
    arbitration_class: str = "cautionary",
    confidence_adjustment: str = "down",
    risk_flags: list[str] | None = None,
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
        "risk_flags": risk_flags or ["early_reversal_likelihood"],
        "source_summary": {
            "accepted_matches": 1,
            "quarantined_matches": 3,
            "analog_matches": 2,
        },
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }


def run_probe() -> dict:
    results: list[dict] = []

    def record_result(case_name: str, status: str, error: str | None = None) -> None:
        entry = {"case": case_name, "status": status}
        if error is not None:
            entry["error"] = error
        results.append(entry)

    # case_01_valid_record_construction
    try:
        refinement_packet = _make_refinement_packet(case_id="case_001")
        record = build_pm_continuity_record(
            refinement_packet=refinement_packet,
            record_id="pmrec_001",
        )
        assert record["artifact_type"] == "pm_continuity_record"
        assert record["sealed"] is True
        assert record["memory_only"] is True
        assert record["runtime_mutation_allowed"] is False
        assert record["execution_influence"] is False
        assert record["recommendation_mutation_allowed"] is False
        record_result("case_01_valid_record_construction", "passed")
    except Exception as exc:
        record_result("case_01_valid_record_construction", "failed", str(exc))

    # case_02_reject_unsealed_refinement_packet
    try:
        refinement_packet = _make_refinement_packet(case_id="case_002")
        refinement_packet["sealed"] = False
        build_pm_continuity_record(
            refinement_packet=refinement_packet,
            record_id="pmrec_002",
        )
        record_result("case_02_reject_unsealed_refinement_packet", "failed", "expected rejection")
    except Exception:
        record_result("case_02_reject_unsealed_refinement_packet", "passed")

    # case_03_reject_runtime_influence_true
    try:
        refinement_packet = _make_refinement_packet(case_id="case_003")
        refinement_packet["execution_influence"] = True
        build_pm_continuity_record(
            refinement_packet=refinement_packet,
            record_id="pmrec_003",
        )
        record_result("case_03_reject_runtime_influence_true", "failed", "expected rejection")
    except Exception:
        record_result("case_03_reject_runtime_influence_true", "passed")

    # case_04_valid_index_creation
    try:
        refinement_packet = _make_refinement_packet(case_id="case_004")
        record = build_pm_continuity_record(
            refinement_packet=refinement_packet,
            record_id="pmrec_004",
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=record,
            index_id="pmidx_001",
            existing_index=None,
        )
        assert index_payload["artifact_type"] == "pm_continuity_index"
        assert index_payload["entry_count"] == 1
        assert index_payload["entries"][0]["continuity_count"] == 1
        record_result("case_04_valid_index_creation", "passed")
    except Exception as exc:
        record_result("case_04_valid_index_creation", "failed", str(exc))

    # case_05_valid_index_accumulation_same_key
    try:
        first_packet = _make_refinement_packet(case_id="case_005_a")
        second_packet = _make_refinement_packet(case_id="case_005_b")
        first_record = build_pm_continuity_record(first_packet, "pmrec_005_a")
        second_record = build_pm_continuity_record(second_packet, "pmrec_005_b")

        index_payload = update_pm_continuity_index(
            pm_continuity_record=first_record,
            index_id="pmidx_002",
            existing_index=None,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=second_record,
            index_id="pmidx_002",
            existing_index=index_payload,
        )

        assert index_payload["entry_count"] == 1
        assert index_payload["entries"][0]["continuity_count"] == 2
        assert index_payload["entries"][0]["last_case_id"] == "case_005_b"
        record_result("case_05_valid_index_accumulation_same_key", "passed")
    except Exception as exc:
        record_result("case_05_valid_index_accumulation_same_key", "failed", str(exc))

    # case_06_valid_index_new_key_branch
    try:
        first_packet = _make_refinement_packet(case_id="case_006_a")
        second_packet = _make_refinement_packet(
            case_id="case_006_b",
            arbitration_class="supportive",
            confidence_adjustment="up",
        )
        first_record = build_pm_continuity_record(first_packet, "pmrec_006_a")
        second_record = build_pm_continuity_record(second_packet, "pmrec_006_b")

        index_payload = update_pm_continuity_index(
            pm_continuity_record=first_record,
            index_id="pmidx_003",
            existing_index=None,
        )
        index_payload = update_pm_continuity_index(
            pm_continuity_record=second_record,
            index_id="pmidx_003",
            existing_index=index_payload,
        )

        assert index_payload["entry_count"] == 2
        record_result("case_06_valid_index_new_key_branch", "passed")
    except Exception as exc:
        record_result("case_06_valid_index_new_key_branch", "failed", str(exc))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())