from __future__ import annotations

from AI_GO.core.runtime.archive.archive_retrieval import (
    ArchiveRetrievalError,
    build_archive_retrieval_result,
)


def _closeout(case_id: str, sealed: bool = True) -> dict:
    return {
        "artifact_type": "case_closeout_record",
        "payload": {
            "case_id": case_id,
            "closeout_state": "closed_accepted",
            "final_state": "success",
            "target_child_core": "proposal_saas",
            "intake_decision": "accepted",
            "created_at": "2026-03-20T00:00:00Z",
            "sealed": sealed,
        },
    }


def _review(case_id: str, sealed: bool = True) -> dict:
    return {
        "artifact_type": "operator_review_view",
        "payload": {
            "case_id": case_id,
            "closeout_state": "closed_accepted",
            "final_state": "success",
            "target_child_core": "proposal_saas",
            "intake_decision": "accepted",
            "created_at": "2026-03-20T00:00:00Z",
            "review_generated_at": "2026-03-20T00:05:00Z",
            "sealed": sealed,
        },
    }


def _review_index(sealed: bool = True) -> dict:
    return {
        "artifact_type": "operator_review_index",
        "payload": {
            "total_count": 2,
            "filtered_count": 2,
            "results": [
                {
                    "case_id": "WR-5903-A",
                    "closeout_state": "closed_accepted",
                    "final_state": "success",
                    "target_child_core": "proposal_saas",
                    "intake_decision": "accepted",
                    "sealed": True,
                }
            ],
            "limit": None,
            "offset": 0,
            "filters": {},
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
    except ArchiveRetrievalError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage59_archive_retrieval_probe():
    results = []

    def case_01_valid_mixed_archive_retrieval():
        out = build_archive_retrieval_result(
            archive_items=[
                _closeout("WR-5901"),
                _review("WR-5902"),
                _review_index(),
            ]
        )
        assert out["artifact_type"] == "archive_retrieval_result"
        assert out["payload"]["total_count"] == 3
        assert out["payload"]["returned_count"] == 3

    results.append(_expect_pass("case_01_valid_mixed_archive_retrieval", case_01_valid_mixed_archive_retrieval))

    def case_02_filter_by_artifact_type():
        out = build_archive_retrieval_result(
            archive_items=[
                _closeout("WR-5902-A"),
                _review("WR-5902-B"),
            ],
            filters={"artifact_type": "operator_review_view"},
        )
        assert out["payload"]["filtered_count"] == 1
        assert out["payload"]["results"][0]["artifact_type"] == "operator_review_view"

    results.append(_expect_pass("case_02_filter_by_artifact_type", case_02_filter_by_artifact_type))

    def case_03_filter_by_case_id():
        out = build_archive_retrieval_result(
            archive_items=[
                _closeout("WR-5903-A"),
                _closeout("WR-5903-B"),
            ],
            filters={"case_id": "WR-5903-B"},
        )
        assert out["payload"]["filtered_count"] == 1
        assert out["payload"]["results"][0]["payload"]["case_id"] == "WR-5903-B"

    results.append(_expect_pass("case_03_filter_by_case_id", case_03_filter_by_case_id))

    def case_04_pagination():
        out = build_archive_retrieval_result(
            archive_items=[
                _closeout("WR-5904-A"),
                _closeout("WR-5904-B"),
                _closeout("WR-5904-C"),
            ],
            limit=2,
            offset=1,
        )
        assert out["payload"]["returned_count"] == 2

    results.append(_expect_pass("case_04_pagination", case_04_pagination))

    def case_05_reject_unsealed_item():
        build_archive_retrieval_result(
            archive_items=[_closeout("WR-5905", sealed=False)]
        )

    results.append(_expect_fail("case_05_reject_unsealed_item", case_05_reject_unsealed_item))

    def case_06_reject_invalid_artifact_type():
        build_archive_retrieval_result(
            archive_items=[{"artifact_type": "case_resolution", "payload": {"sealed": True}}]
        )

    results.append(_expect_fail("case_06_reject_invalid_artifact_type", case_06_reject_invalid_artifact_type))

    def case_07_reject_invalid_filter_field():
        build_archive_retrieval_result(
            archive_items=[_closeout("WR-5907")],
            filters={"unknown_field": "x"},
        )

    results.append(_expect_fail("case_07_reject_invalid_filter_field", case_07_reject_invalid_filter_field))

    def case_08_reject_negative_offset():
        build_archive_retrieval_result(
            archive_items=[_closeout("WR-5908")],
            offset=-1,
        )

    results.append(_expect_fail("case_08_reject_negative_offset", case_08_reject_negative_offset))

    def case_09_reject_invalid_limit():
        build_archive_retrieval_result(
            archive_items=[_closeout("WR-5909")],
            limit=0,
        )

    results.append(_expect_fail("case_09_reject_invalid_limit", case_09_reject_invalid_limit))

    def case_10_reject_internal_field_leakage():
        bad = _review("WR-5910")
        bad["payload"]["_internal"] = {"unsafe": True}
        build_archive_retrieval_result(
            archive_items=[bad]
        )

    results.append(_expect_fail("case_10_reject_internal_field_leakage", case_10_reject_internal_field_leakage))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage59_archive_retrieval_probe())