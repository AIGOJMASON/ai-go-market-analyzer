from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.ingress_processor import (
    IngressValidationError,
    process_ingress,
)


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def _valid_packet() -> dict:
    return {
        "artifact_type": "pm_decision_packet",
        "dispatched_by": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "dispatch_id": "DISPATCH-001",
        "source": "validated_upstream",
        "receipt": {"receipt_id": "RCPT-001"},
        "payload": {
            "conditioning": {"holding_window_hours": 24},
            "market_context": {
                "volatility_level": "medium",
                "liquidity_level": "high",
                "stress_level": "medium",
            },
            "event": {
                "event_id": "EVT-001",
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


def main() -> dict:
    results = []

    packet = _valid_packet()
    try:
        normalized = process_ingress(packet)
        ok = normalized.get("ingress_valid") is True and normalized.get("core_id") == "market_analyzer_v1"
        results.append(
            _result(
                "case_01_valid_ingress_packet",
                "passed" if ok else "failed",
                None if ok else "normalized ingress missing expected fields",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_valid_ingress_packet", "failed", str(exc)))

    packet = _valid_packet()
    packet.pop("receipt")
    try:
        process_ingress(packet)
        results.append(_result("case_02_reject_missing_receipt", "failed", "accepted packet without receipt"))
    except IngressValidationError:
        results.append(_result("case_02_reject_missing_receipt", "passed"))

    packet = _valid_packet()
    packet["dispatched_by"] = "RESEARCH_CORE"
    try:
        process_ingress(packet)
        results.append(_result("case_03_reject_non_pm_dispatch", "failed", "accepted non-PM dispatch"))
    except IngressValidationError:
        results.append(_result("case_03_reject_non_pm_dispatch", "passed"))

    packet = _valid_packet()
    packet["target_core"] = "other_core"
    try:
        process_ingress(packet)
        results.append(_result("case_04_reject_target_core_mismatch", "failed", "accepted target mismatch"))
    except IngressValidationError:
        results.append(_result("case_04_reject_target_core_mismatch", "passed"))

    packet = _valid_packet()
    packet["source"] = "raw_research_core_output"
    try:
        process_ingress(packet)
        results.append(_result("case_05_reject_raw_research_source", "failed", "accepted raw research source"))
    except IngressValidationError:
        results.append(_result("case_05_reject_raw_research_source", "passed"))

    packet = _valid_packet()
    packet["artifact_type"] = "unknown_packet"
    try:
        process_ingress(packet)
        results.append(_result("case_06_reject_invalid_artifact_type", "failed", "accepted invalid artifact_type"))
    except IngressValidationError:
        results.append(_result("case_06_reject_invalid_artifact_type", "passed"))

    packet = _valid_packet()
    packet["payload"] = []
    try:
        process_ingress(packet)
        results.append(_result("case_07_reject_non_dict_payload", "failed", "accepted non-dict payload"))
    except IngressValidationError:
        results.append(_result("case_07_reject_non_dict_payload", "passed"))

    packet = _valid_packet()
    packet["payload"]["candidates"] = "XLE"
    try:
        process_ingress(packet)
        results.append(_result("case_08_reject_non_list_candidates", "failed", "accepted non-list candidates"))
    except IngressValidationError:
        results.append(_result("case_08_reject_non_list_candidates", "passed"))

    packet = _valid_packet()
    packet["payload"]["candidates"] = ["XLE"]
    try:
        process_ingress(packet)
        results.append(_result("case_09_reject_non_dict_candidate", "failed", "accepted non-dict candidate"))
    except IngressValidationError:
        results.append(_result("case_09_reject_non_dict_candidate", "passed"))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())