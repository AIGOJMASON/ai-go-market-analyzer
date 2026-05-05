from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.run import (
    MarketAnalyzerRuntimeError,
    run,
)


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def _base_packet() -> dict:
    return {
        "artifact_type": "pm_decision_packet",
        "dispatched_by": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "dispatch_id": "DISPATCH-RT-001",
        "source": "validated_upstream",
        "receipt": {"receipt_id": "RCPT-RT-001"},
        "payload": {
            "conditioning": {"holding_window_hours": 24},
            "market_context": {
                "volatility_level": "medium",
                "liquidity_level": "high",
                "stress_level": "medium",
            },
            "event": {
                "event_id": "EVT-RT-001",
                "event_type": "supply_shock",
                "propagation_speed": "fast",
                "ripple_depth": "primary",
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
                    "entry_signal": "confirmation_reclaim",
                    "exit_rule": "quick_exit_on_rebound_completion",
                },
                {
                    "symbol": "NTR",
                    "sector": "fertilizer",
                    "liquidity": "medium",
                    "stabilization": True,
                    "reclaim": True,
                    "confirmation": True,
                },
            ],
        },
    }


def main() -> dict:
    results = []

    packet = _base_packet()
    try:
        outcome = run(packet)
        artifacts = outcome.get("artifacts", {})
        ok = (
            outcome.get("status") == "ok"
            and "trade_recommendation_packet" in artifacts
            and "approval_request_packet" in artifacts
            and artifacts["trade_recommendation_packet"].get("recommendation_count") == 2
        )
        results.append(
            _result(
                "case_01_valid_runtime_flow",
                "passed" if ok else "failed",
                None if ok else "runtime result missing expected artifacts",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_valid_runtime_flow", "failed", str(exc)))

    packet = _base_packet()
    packet["payload"]["event"]["shock_confirmed"] = False
    try:
        run(packet)
        results.append(_result("case_02_reject_missing_shock_confirmation", "failed", "accepted unconfirmed shock"))
    except MarketAnalyzerRuntimeError:
        results.append(_result("case_02_reject_missing_shock_confirmation", "passed"))

    packet = _base_packet()
    packet["payload"]["candidates"] = [
        {
            "symbol": "TSLA",
            "sector": "automotive",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
        }
    ]
    try:
        run(packet)
        results.append(_result("case_03_reject_non_necessity_candidates", "failed", "accepted non-necessity sector"))
    except MarketAnalyzerRuntimeError:
        results.append(_result("case_03_reject_non_necessity_candidates", "passed"))

    packet = _base_packet()
    packet["payload"]["candidates"] = [
        {
            "symbol": "XLE",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": False,
            "confirmation": True,
        }
    ]
    try:
        run(packet)
        results.append(_result("case_04_reject_failed_rebound_validation", "failed", "accepted failed rebound"))
    except MarketAnalyzerRuntimeError:
        results.append(_result("case_04_reject_failed_rebound_validation", "passed"))

    packet = _base_packet()
    packet["payload"]["market_context"]["volatility_level"] = "extreme"
    packet["payload"]["market_context"]["stress_level"] = "extreme"
    try:
        outcome = run(packet)
        regime = outcome["artifacts"]["market_regime_record"]
        ok = regime.get("regime") == "crisis" and regime.get("trade_posture") == "conditional"
        results.append(
            _result(
                "case_05_crisis_regime_classification",
                "passed" if ok else "failed",
                None if ok else "crisis regime classification mismatch",
            )
        )
    except Exception as exc:
        results.append(_result("case_05_crisis_regime_classification", "failed", str(exc)))

    packet = _base_packet()
    packet["payload"]["event"]["propagation_speed"] = "invalid"
    packet["payload"]["event"]["ripple_depth"] = "invalid"
    try:
        outcome = run(packet)
        propagation = outcome["artifacts"]["event_propagation_record"]
        ok = propagation.get("propagation_speed") == "medium" and propagation.get("ripple_depth") == "primary"
        results.append(
            _result(
                "case_06_invalid_propagation_defaults",
                "passed" if ok else "failed",
                None if ok else "propagation defaults not applied",
            )
        )
    except Exception as exc:
        results.append(_result("case_06_invalid_propagation_defaults", "failed", str(exc)))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())