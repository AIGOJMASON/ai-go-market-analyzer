from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.scenario_runner import run_all_scenarios


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def main() -> dict:
    results = []

    try:
        report = run_all_scenarios()
        ok = report.get("failed", 0) == 0 and report.get("passed", 0) == 6
        results.append(
            _result(
                "case_01_all_scenarios_match_expectations",
                "passed" if ok else "failed",
                None if ok else f"scenario report mismatch: {report}",
            )
        )
    except Exception as exc:
        results.append(
            _result(
                "case_01_all_scenarios_match_expectations",
                "failed",
                str(exc),
            )
        )

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())