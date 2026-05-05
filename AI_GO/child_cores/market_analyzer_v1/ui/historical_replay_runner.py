from __future__ import annotations

from typing import Any

from AI_GO.child_cores.market_analyzer_v1.execution.run import (
    MarketAnalyzerRuntimeError,
    run,
)
from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import build_output_views
from AI_GO.child_cores.market_analyzer_v1.ui.historical_replay_expectations import (
    build_historical_replay_expectations,
)
from AI_GO.child_cores.market_analyzer_v1.ui.historical_replay_packets import (
    clone_replay_packets,
)
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _extract_recommendations(runtime_result: dict, output_views: dict | None = None) -> list[dict]:
    artifacts = _as_dict(runtime_result.get("artifacts"))
    recommendation_packet = _as_dict(artifacts.get("trade_recommendation_packet"))

    candidate_paths = [
        recommendation_packet.get("recommendations"),
        runtime_result.get("recommendations"),
        _as_dict(runtime_result.get("payload")).get("recommendations"),
        _as_dict(runtime_result.get("result")).get("recommendations"),
        _as_dict(runtime_result.get("runtime")).get("recommendations"),
    ]

    if output_views is not None:
        views = _as_dict(output_views.get("views"))
        recommendations_view = _as_dict(views.get("recommendations"))
        candidate_paths.extend(
            [
                recommendations_view.get("items"),
                output_views.get("recommendations"),
                _as_dict(output_views.get("dashboard")).get("recommendations"),
                _as_dict(output_views.get("summary")).get("recommendations"),
                _as_dict(output_views.get("payload")).get("recommendations"),
            ]
        )

    for maybe_list in candidate_paths:
        if isinstance(maybe_list, list):
            return [item for item in maybe_list if isinstance(item, dict)]

    return []


def _extract_symbols(recommendations: list[dict]) -> list[str]:
    symbols: list[str] = []
    for item in recommendations:
        symbol = item.get("symbol")
        if isinstance(symbol, str) and symbol:
            symbols.append(symbol)
    return symbols


def _extract_execution_allowed(runtime_result: dict, output_views: dict | None = None) -> bool | None:
    artifacts = _as_dict(runtime_result.get("artifacts"))
    recommendation_packet = _as_dict(artifacts.get("trade_recommendation_packet"))
    approval_packet = _as_dict(artifacts.get("approval_request_packet"))

    candidate_values = [
        recommendation_packet.get("execution_allowed"),
        approval_packet.get("execution_allowed"),
        runtime_result.get("execution_allowed"),
        _as_dict(runtime_result.get("payload")).get("execution_allowed"),
        _as_dict(runtime_result.get("result")).get("execution_allowed"),
    ]

    if output_views is not None:
        views = _as_dict(output_views.get("views"))
        recommendations_view = _as_dict(views.get("recommendations"))
        approval_view = _as_dict(views.get("approval_gate"))
        candidate_values.extend(
            [
                recommendations_view.get("execution_allowed"),
                approval_view.get("execution_allowed"),
                output_views.get("execution_allowed"),
                _as_dict(output_views.get("dashboard")).get("execution_allowed"),
                _as_dict(output_views.get("payload")).get("execution_allowed"),
            ]
        )

    for value in candidate_values:
        if isinstance(value, bool):
            return value

    return None


def _watcher_passed(watcher_result: Any) -> bool:
    if isinstance(watcher_result, bool):
        return watcher_result
    if isinstance(watcher_result, dict):
        for key in ("passed", "watcher_passed", "valid", "approved"):
            value = watcher_result.get(key)
            if isinstance(value, bool):
                return value
    return False


def _runtime_failure_case(packet: dict, expectation: dict, error: Exception) -> dict:
    expected_error_fragment = expectation.get("expected_runtime_error_contains")
    error_text = str(error)

    errors: list[str] = []
    status = "passed"

    if isinstance(expected_error_fragment, str):
        if expected_error_fragment not in error_text:
            status = "failed"
            errors.append(
                f"runtime_error mismatch: expected fragment {expected_error_fragment!r}, got {error_text!r}"
            )
    else:
        status = "failed"
        errors.append(f"unexpected runtime_error: {error_text}")

    return {
        "case": expectation.get("name", packet.get("dispatch_id", "unknown_case")),
        "dispatch_id": packet.get("dispatch_id"),
        "status": status,
        "should_succeed": bool(expectation.get("should_succeed")),
        "actual_success": False,
        "recommendation_count": 0,
        "recommendation_symbols": [],
        "watcher_passed": None,
        "execution_allowed": None,
        "errors": errors,
        "runtime_error": error_text,
        "runtime_result": None,
        "watcher_result": None,
        "output_views": None,
    }


def _evaluate_case(packet: dict, expectation: dict) -> dict:
    try:
        runtime_result = run(packet)
    except MarketAnalyzerRuntimeError as error:
        return _runtime_failure_case(packet, expectation, error)

    watcher_result = verify_runtime_result(runtime_result)
    output_views = build_output_views(runtime_result)

    recommendations = _extract_recommendations(runtime_result, output_views)
    recommendation_symbols = _extract_symbols(recommendations)
    recommendation_count = len(recommendations)
    watcher_passed = _watcher_passed(watcher_result)
    execution_allowed = _extract_execution_allowed(runtime_result, output_views)

    errors: list[str] = []

    should_succeed = bool(expectation.get("should_succeed"))
    min_count = expectation.get("minimum_recommendation_count")
    max_count = expectation.get("maximum_recommendation_count")
    expected_any = expectation.get("expected_symbols_any_of", [])
    forbidden_symbols = expectation.get("forbidden_symbols", [])
    watcher_should_pass = expectation.get("watcher_should_pass")
    execution_allowed_must_be = expectation.get("execution_allowed_must_be")

    actual_success = recommendation_count > 0

    if should_succeed and not actual_success:
        errors.append("expected at least one recommendation but none were produced")
    if not should_succeed and actual_success:
        errors.append("expected no recommendation but recommendation(s) were produced")

    if isinstance(min_count, int) and recommendation_count < min_count:
        errors.append(
            f"recommendation_count {recommendation_count} is below minimum {min_count}"
        )

    if isinstance(max_count, int) and recommendation_count > max_count:
        errors.append(
            f"recommendation_count {recommendation_count} exceeds maximum {max_count}"
        )

    if expected_any:
        if not any(symbol in recommendation_symbols for symbol in expected_any):
            errors.append(
                f"expected one of symbols {expected_any} but got {recommendation_symbols}"
            )

    if forbidden_symbols:
        found_forbidden = [s for s in recommendation_symbols if s in forbidden_symbols]
        if found_forbidden:
            errors.append(f"forbidden symbols present: {found_forbidden}")

    if isinstance(watcher_should_pass, bool) and watcher_passed != watcher_should_pass:
        errors.append(
            f"watcher_passed {watcher_passed} does not match expected {watcher_should_pass}"
        )

    if isinstance(execution_allowed_must_be, bool):
        if execution_allowed is None:
            errors.append("execution_allowed could not be extracted")
        elif execution_allowed != execution_allowed_must_be:
            errors.append(
                f"execution_allowed {execution_allowed} does not match required {execution_allowed_must_be}"
            )

    return {
        "case": expectation.get("name", packet.get("dispatch_id", "unknown_case")),
        "dispatch_id": packet.get("dispatch_id"),
        "status": "passed" if not errors else "failed",
        "should_succeed": should_succeed,
        "actual_success": actual_success,
        "recommendation_count": recommendation_count,
        "recommendation_symbols": recommendation_symbols,
        "watcher_passed": watcher_passed,
        "execution_allowed": execution_allowed,
        "errors": errors,
        "runtime_error": None,
        "runtime_result": runtime_result,
        "watcher_result": watcher_result,
        "output_views": output_views,
    }


def run_historical_replay() -> dict:
    packets = clone_replay_packets()
    expectations = build_historical_replay_expectations()
    results: list[dict] = []

    for packet in packets:
        dispatch_id = packet.get("dispatch_id")
        expectation = expectations.get(dispatch_id)
        if expectation is None:
            results.append(
                {
                    "case": dispatch_id or "unknown_dispatch_id",
                    "dispatch_id": dispatch_id,
                    "status": "failed",
                    "should_succeed": None,
                    "actual_success": None,
                    "recommendation_count": 0,
                    "recommendation_symbols": [],
                    "watcher_passed": None,
                    "execution_allowed": None,
                    "errors": [f"missing expectation for dispatch_id={dispatch_id}"],
                    "runtime_error": None,
                    "runtime_result": None,
                    "watcher_result": None,
                    "output_views": None,
                }
            )
            continue

        results.append(_evaluate_case(packet, expectation))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


def main() -> None:
    print(run_historical_replay())


if __name__ == "__main__":
    main()