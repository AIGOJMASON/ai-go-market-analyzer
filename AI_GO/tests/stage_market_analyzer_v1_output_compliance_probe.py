from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import (
    OutputBuilderError,
    build_output_views,
)
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def _runtime_result() -> dict:
    packet = {
        "artifact_type": "pm_decision_packet",
        "dispatched_by": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "dispatch_id": "DISPATCH-OUT-001",
        "source": "validated_upstream",
        "receipt": {"receipt_id": "RCPT-OUT-001"},
        "payload": {
            "conditioning": {"holding_window_hours": 24},
            "market_context": {
                "volatility_level": "medium",
                "liquidity_level": "high",
                "stress_level": "medium",
            },
            "event": {
                "event_id": "EVT-OUT-001",
                "event_type": "supply_shock",
                "propagation_speed": "fast",
                "ripple_depth": "secondary",
                "shock_confirmed": True,
            },
            "macro_bias": {"direction": "neutral"},
            "candidates": [
                {
                    "symbol": "XLE",
                    "sector": "energy",
                    "liquidity": "high",
                    "stabilization": True,
                    "reclaim": True,
                    "confirmation": True,
                }
            ],
        },
    }
    return run(packet)


def main() -> dict:
    results = []

    try:
        runtime_result = _runtime_result()
        output = build_output_views(runtime_result)
        expected_panels = {
            "market_regime",
            "active_events",
            "watchlist",
            "recommendations",
            "approval_gate",
            "receipt_trace",
        }
        actual_panels = set(output.get("views", {}).keys())
        ok = output.get("artifact_type") == "market_dashboard_output" and expected_panels == actual_panels
        results.append(
            _result(
                "case_01_valid_dashboard_output",
                "passed" if ok else "failed",
                None if ok else f"panel mismatch: {actual_panels}",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_valid_dashboard_output", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        views = build_output_views(runtime_result)["views"]
        recommendations = views["recommendations"]
        items = recommendations.get("items", [])
        ok = bool(items) and all("narrative" not in item for item in items)
        results.append(
            _result(
                "case_02_recommendation_view_non_narrative",
                "passed" if ok else "failed",
                None if ok else "recommendation items contain unexpected narrative fields",
            )
        )
    except Exception as exc:
        results.append(_result("case_02_recommendation_view_non_narrative", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        receipt_view = build_output_views(runtime_result)["views"]["receipt_trace"]
        ok = bool(receipt_view.get("upstream_receipt")) and isinstance(receipt_view.get("trace"), dict)
        results.append(
            _result(
                "case_03_receipt_trace_present",
                "passed" if ok else "failed",
                None if ok else "receipt trace missing required content",
            )
        )
    except Exception as exc:
        results.append(_result("case_03_receipt_trace_present", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        del runtime_result["artifacts"]["approval_request_packet"]
        build_output_views(runtime_result)
        results.append(_result("case_04_reject_missing_required_artifact", "failed", "accepted missing artifact"))
    except OutputBuilderError:
        results.append(_result("case_04_reject_missing_required_artifact", "passed"))
    except Exception as exc:
        results.append(_result("case_04_reject_missing_required_artifact", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        watcher_result = verify_runtime_result(runtime_result)
        ok = watcher_result.get("watcher_passed") is True and watcher_result.get("watcher_receipt") is not None
        results.append(
            _result(
                "case_05_watcher_verifies_valid_output",
                "passed" if ok else "failed",
                None if ok else "watcher did not verify valid output",
            )
        )
    except Exception as exc:
        results.append(_result("case_05_watcher_verifies_valid_output", "failed", str(exc)))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())