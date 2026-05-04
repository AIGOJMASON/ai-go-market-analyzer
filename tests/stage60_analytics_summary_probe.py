from __future__ import annotations

from AI_GO.core.runtime.analytics.analytics_summary import (
    AnalyticsSummaryError,
    build_analytics_summary,
)


def _closeout(case_id: str, closeout_state: str = "closed_accepted", intake_decision: str = "accepted"):
    return {
        "artifact_type": "case_closeout_record",
        "payload": {
            "case_id": case_id,
            "closeout_state": closeout_state,
            "final_state": "success",
            "target_child_core": "proposal_saas",
            "intake_decision": intake_decision,
            "created_at": "2026-03-20T00:00:00Z",
            "sealed": True,
        },
    }


def _review(case_id: str, intake_decision: str = "accepted", target_child_core: str = "proposal_saas"):
    return {
        "artifact_type": "operator_review_view",
        "payload": {
            "case_id": case_id,
            "closeout_state": "closed_accepted",
            "final_state": "success",
            "target_child_core": target_child_core,
            "intake_decision": intake_decision,
            "created_at": "2026-03-20T00:00:00Z",
            "review_generated_at": "2026-03-20T00:05:00Z",
            "sealed": True,
        },
    }


def _retrieval(results, sealed: bool = True):
    return {
        "artifact_type": "archive_retrieval_result",
        "payload": {
            "issuing_authority": "RUNTIME_ARCHIVE_RETRIEVAL",
            "total_count": len(results),
            "filtered_count": len(results),
            "returned_count": len(results),
            "results": results,
            "filters": {},
            "limit": None,
            "offset": 0,
            "sealed": sealed,
        },
    }


def _expect_pass(name, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def _expect_fail(name, fn):
    try:
        fn()
        return {"case": name, "status": "failed", "error": "expected failure but passed"}
    except AnalyticsSummaryError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage60_analytics_summary_probe():
    results = []

    def case_01_valid_summary_from_mixed_results():
        out = build_analytics_summary(
            _retrieval(
                [
                    _closeout("WR-6001-A"),
                    _review("WR-6001-B", target_child_core="gis"),
                ]
            )
        )
        assert out["artifact_type"] == "analytics_summary"
        assert out["payload"]["total_items_in_scope"] == 2

    results.append(_expect_pass("case_01_valid_summary_from_mixed_results", case_01_valid_summary_from_mixed_results))

    def case_02_counts_by_closeout_and_intake():
        out = build_analytics_summary(
            _retrieval(
                [
                    _closeout("WR-6002-A", closeout_state="closed_accepted", intake_decision="accepted"),
                    _closeout("WR-6002-B", closeout_state="closed_rejected", intake_decision="rejected"),
                ]
            )
        )
        assert out["payload"]["counts_by_closeout_state"]["closed_accepted"] == 1
        assert out["payload"]["counts_by_closeout_state"]["closed_rejected"] == 1
        assert out["payload"]["counts_by_intake_decision"]["accepted"] == 1
        assert out["payload"]["counts_by_intake_decision"]["rejected"] == 1

    results.append(_expect_pass("case_02_counts_by_closeout_and_intake", case_02_counts_by_closeout_and_intake))

    def case_03_pattern_notes_present():
        out = build_analytics_summary(
            _retrieval(
                [
                    _review("WR-6003-A", intake_decision="accepted", target_child_core="proposal_saas"),
                    _review("WR-6003-B", intake_decision="accepted", target_child_core="proposal_saas"),
                ]
            )
        )
        assert "accepted_intake_majority" in out["payload"]["pattern_notes"]
        assert "single_child_core_scope:proposal_saas" in out["payload"]["pattern_notes"]

    results.append(_expect_pass("case_03_pattern_notes_present", case_03_pattern_notes_present))

    def case_04_reject_unsealed_retrieval_result():
        build_analytics_summary(
            _retrieval([_closeout("WR-6004")], sealed=False)
        )

    results.append(_expect_fail("case_04_reject_unsealed_retrieval_result", case_04_reject_unsealed_retrieval_result))

    def case_05_reject_invalid_retrieval_artifact_type():
        build_analytics_summary(
            {"artifact_type": "operator_review_index", "payload": {"sealed": True, "results": []}}
        )

    results.append(_expect_fail("case_05_reject_invalid_retrieval_artifact_type", case_05_reject_invalid_retrieval_artifact_type))

    def case_06_reject_invalid_result_item_type():
        build_analytics_summary(
            _retrieval(
                [
                    {"artifact_type": "case_resolution", "payload": {"sealed": True}}
                ]
            )
        )

    results.append(_expect_fail("case_06_reject_invalid_result_item_type", case_06_reject_invalid_result_item_type))

    def case_07_reject_unsealed_result_item():
        bad = _review("WR-6007")
        bad["payload"]["sealed"] = False
        build_analytics_summary(_retrieval([bad]))

    results.append(_expect_fail("case_07_reject_unsealed_result_item", case_07_reject_unsealed_result_item))

    def case_08_reject_missing_results_list():
        build_analytics_summary(
            {
                "artifact_type": "archive_retrieval_result",
                "payload": {
                    "sealed": True,
                },
            }
        )

    results.append(_expect_fail("case_08_reject_missing_results_list", case_08_reject_missing_results_list))

    def case_09_reject_internal_field_leakage():
        bad = _review("WR-6009")
        bad["payload"]["_internal"] = {"unsafe": True}
        build_analytics_summary(_retrieval([bad]))

    results.append(_expect_fail("case_09_reject_internal_field_leakage", case_09_reject_internal_field_leakage))

    def case_10_zero_items_supported():
        out = build_analytics_summary(_retrieval([]))
        assert out["payload"]["total_items_in_scope"] == 0
        assert "no_items_in_scope" in out["payload"]["pattern_notes"]

    results.append(_expect_pass("case_10_zero_items_supported", case_10_zero_items_supported))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage60_analytics_summary_probe())