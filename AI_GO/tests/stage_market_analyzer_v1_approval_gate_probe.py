from __future__ import annotations

from copy import deepcopy

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
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
        "dispatch_id": "DISPATCH-APP-001",
        "source": "validated_upstream",
        "receipt": {"receipt_id": "RCPT-APP-001"},
        "payload": {
            "conditioning": {"holding_window_hours": 24},
            "market_context": {
                "volatility_level": "medium",
                "liquidity_level": "high",
                "stress_level": "medium",
            },
            "event": {
                "event_id": "EVT-APP-001",
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
                }
            ],
        },
    }
    return run(packet)


def main() -> dict:
    results = []

    try:
        runtime_result = _runtime_result()
        packet = runtime_result["artifacts"]["trade_recommendation_packet"]
        ok = (
            packet.get("execution_allowed") is False
            and packet.get("approval_gate") == "human_trade_approval_record"
            and packet.get("recommendation_count") == 1
        )
        results.append(
            _result(
                "case_01_trade_packet_requires_approval",
                "passed" if ok else "failed",
                None if ok else "recommendation packet approval gate mismatch",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_trade_packet_requires_approval", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        approval_packet = runtime_result["artifacts"]["approval_request_packet"]
        ok = (
            approval_packet.get("approval_type") == "human_trade_approval_record"
            and approval_packet.get("execution_allowed") is False
        )
        results.append(
            _result(
                "case_02_approval_request_preserves_execution_block",
                "passed" if ok else "failed",
                None if ok else "approval request packet mismatch",
            )
        )
    except Exception as exc:
        results.append(_result("case_02_approval_request_preserves_execution_block", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        tampered = deepcopy(runtime_result)
        tampered["artifacts"]["trade_recommendation_packet"]["execution_allowed"] = True
        watcher_result = verify_runtime_result(tampered)
        ok = watcher_result.get("watcher_passed") is False
        results.append(
            _result(
                "case_03_watcher_rejects_execution_enabled_trade_packet",
                "passed" if ok else "failed",
                None if ok else "watcher accepted execution_enabled recommendation",
            )
        )
    except Exception as exc:
        results.append(_result("case_03_watcher_rejects_execution_enabled_trade_packet", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        tampered = deepcopy(runtime_result)
        tampered["artifacts"]["approval_request_packet"]["approval_type"] = "auto_execute"
        watcher_result = verify_runtime_result(tampered)
        ok = watcher_result.get("watcher_passed") is False
        results.append(
            _result(
                "case_04_watcher_rejects_invalid_approval_type",
                "passed" if ok else "failed",
                None if ok else "watcher accepted invalid approval type",
            )
        )
    except Exception as exc:
        results.append(_result("case_04_watcher_rejects_invalid_approval_type", "failed", str(exc)))

    try:
        runtime_result = _runtime_result()
        tampered = deepcopy(runtime_result)
        tampered["artifacts"]["receipt_trace_packet"]["upstream_receipt"] = None
        watcher_result = verify_runtime_result(tampered)
        ok = watcher_result.get("watcher_passed") is False
        results.append(
            _result(
                "case_05_watcher_rejects_missing_receipt",
                "passed" if ok else "failed",
                None if ok else "watcher accepted missing receipt",
            )
        )
    except Exception as exc:
        results.append(_result("case_05_watcher_rejects_missing_receipt", "failed", str(exc)))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())