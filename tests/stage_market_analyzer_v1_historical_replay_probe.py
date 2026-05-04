from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.historical_replay_runner import (
    run_historical_replay,
)


def run_probe() -> dict:
    replay_result = run_historical_replay()
    replay_cases = replay_result.get("results", [])

    results: list[dict] = []

    case_01_pass = isinstance(replay_result, dict)
    results.append(
        {
            "case": "case_01_valid_replay_result_dict",
            "status": "passed" if case_01_pass else "failed",
        }
    )

    case_02_pass = (
        isinstance(replay_result.get("passed"), int)
        and isinstance(replay_result.get("failed"), int)
    )
    results.append(
        {
            "case": "case_02_has_pass_fail_counters",
            "status": "passed" if case_02_pass else "failed",
        }
    )

    case_03_pass = isinstance(replay_cases, list) and len(replay_cases) == 6
    results.append(
        {
            "case": "case_03_expected_case_count",
            "status": "passed" if case_03_pass else "failed",
        }
    )

    required_keys = {
        "case",
        "dispatch_id",
        "status",
        "should_succeed",
        "actual_success",
        "recommendation_count",
        "recommendation_symbols",
        "watcher_passed",
        "execution_allowed",
        "errors",
        "runtime_error",
    }
    case_04_pass = True
    for item in replay_cases:
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            case_04_pass = False
            break
    results.append(
        {
            "case": "case_04_result_item_structure_valid",
            "status": "passed" if case_04_pass else "failed",
        }
    )

    positive_ids = {"HIST-REPLAY-001", "HIST-REPLAY-004", "HIST-REPLAY-005"}
    positive_cases = [item for item in replay_cases if item.get("dispatch_id") in positive_ids]
    case_05_pass = all(item.get("watcher_passed") is True for item in positive_cases)
    results.append(
        {
            "case": "case_05_positive_cases_watcher_passed",
            "status": "passed" if case_05_pass else "failed",
        }
    )

    negative_ids = {"HIST-REPLAY-002", "HIST-REPLAY-003", "HIST-REPLAY-006"}
    negative_cases = [item for item in replay_cases if item.get("dispatch_id") in negative_ids]
    case_06_pass = all(item.get("status") == "passed" for item in negative_cases)
    results.append(
        {
            "case": "case_06_negative_runtime_error_cases_are_accepted",
            "status": "passed" if case_06_pass else "failed",
        }
    )

    crisis_cases = [item for item in replay_cases if item.get("dispatch_id") == "HIST-REPLAY-004"]
    case_07_pass = (
        len(crisis_cases) == 1
        and crisis_cases[0].get("execution_allowed") is False
        and crisis_cases[0].get("recommendation_count", 0) >= 1
    )
    results.append(
        {
            "case": "case_07_crisis_case_keeps_execution_blocked",
            "status": "passed" if case_07_pass else "failed",
        }
    )

    rejection_counts_ok = True
    for item in negative_cases:
        if item.get("recommendation_count") != 0:
            rejection_counts_ok = False
            break
    results.append(
        {
            "case": "case_08_rejection_cases_have_zero_recommendations",
            "status": "passed" if rejection_counts_ok else "failed",
        }
    )

    mixed_cases = [item for item in replay_cases if item.get("dispatch_id") == "HIST-REPLAY-005"]
    case_09_pass = (
        len(mixed_cases) == 1
        and "QQQ" not in mixed_cases[0].get("recommendation_symbols", [])
        and mixed_cases[0].get("recommendation_count", 0) >= 1
    )
    results.append(
        {
            "case": "case_09_mixed_case_filters_forbidden_symbol",
            "status": "passed" if case_09_pass else "failed",
        }
    )

    case_10_pass = all(item.get("status") == "passed" for item in replay_cases)
    results.append(
        {
            "case": "case_10_all_replay_cases_pass",
            "status": "passed" if case_10_pass else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())