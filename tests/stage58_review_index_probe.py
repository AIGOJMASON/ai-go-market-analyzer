from AI_GO.core.runtime.review.review_index import (
    ReviewIndexError,
    build_operator_review_index,
)


def _view(case_id, decision="accepted"):
    return {
        "artifact_type": "operator_review_view",
        "payload": {
            "case_id": case_id,
            "closeout_state": "closed_accepted",
            "final_state": "success",
            "target_child_core": "proposal_saas",
            "intake_decision": decision,
            "created_at": "2026-03-20T00:00:00Z",
            "sealed": True,
        },
    }


def _expect_pass(name, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except Exception as e:
        return {"case": name, "status": "failed", "error": str(e)}


def _expect_fail(name, fn):
    try:
        fn()
        return {"case": name, "status": "failed"}
    except ReviewIndexError:
        return {"case": name, "status": "passed"}


def run_stage58_review_index_probe():
    results = []

    def case_01_valid_index():
        out = build_operator_review_index([_view("1"), _view("2")])
        assert out["artifact_type"] == "operator_review_index"
        assert out["payload"]["total_count"] == 2

    results.append(_expect_pass("case_01_valid_index", case_01_valid_index))

    def case_02_filter():
        out = build_operator_review_index(
            [_view("1", "accepted"), _view("2", "rejected")],
            filters={"intake_decision": "accepted"},
        )
        assert out["payload"]["filtered_count"] == 1

    results.append(_expect_pass("case_02_filter", case_02_filter))

    def case_03_pagination():
        out = build_operator_review_index(
            [_view("1"), _view("2"), _view("3")],
            limit=2,
            offset=1,
        )
        assert len(out["payload"]["results"]) == 2

    results.append(_expect_pass("case_03_pagination", case_03_pagination))

    def case_04_reject_unsealed():
        bad = _view("4")
        bad["payload"]["sealed"] = False
        build_operator_review_index([bad])

    results.append(_expect_fail("case_04_reject_unsealed", case_04_reject_unsealed))

    def case_05_reject_wrong_type():
        build_operator_review_index([{"artifact_type": "case_closeout_record"}])

    results.append(_expect_fail("case_05_reject_wrong_type", case_05_reject_wrong_type))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage58_review_index_probe())