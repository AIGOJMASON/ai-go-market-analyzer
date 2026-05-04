from AI_GO.core.runtime.review.operator_review_view import (
    OperatorReviewError,
    build_operator_review_view,
)


def _closeout(case_id: str, sealed: bool = True):
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
    except OperatorReviewError:
        return {"case": name, "status": "passed"}


def run_stage57_operator_review_probe():
    results = []

    def case_01_valid():
        out = build_operator_review_view(_closeout("WR-5701"))
        assert out["artifact_type"] == "operator_review_view"

    results.append(_expect_pass("case_01_valid", case_01_valid))

    def case_02_reject_unsealed():
        build_operator_review_view(_closeout("WR-5702", sealed=False))

    results.append(_expect_fail("case_02_reject_unsealed", case_02_reject_unsealed))

    def case_03_reject_wrong_type():
        build_operator_review_view({"artifact_type": "case_resolution", "payload": {}})

    results.append(_expect_fail("case_03_reject_wrong_type", case_03_reject_wrong_type))

    def case_04_reject_missing_field():
        bad = _closeout("WR-5704")
        del bad["payload"]["case_id"]
        build_operator_review_view(bad)

    results.append(_expect_fail("case_04_reject_missing_field", case_04_reject_missing_field))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage57_operator_review_probe())