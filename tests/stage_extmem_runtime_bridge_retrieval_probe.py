from __future__ import annotations

import json
import traceback

from AI_GO.EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
    run_external_memory_runtime_path,
)


def _strong_payload() -> dict:
    return {
        "request_id": "TEST-BRIDGE-RETRIEVAL-001",
        "symbol": "XLE",
        "headline": "Confirmed major oil infrastructure disruption impacting supply chains globally",
        "price_change_pct": 3.5,
        "sector": "energy",
        "confirmation": "confirmed",
        "event_theme": "energy_rebound",
        "macro_bias": "supportive",
        "route_mode": "pm_route",
        "source_type": "live_market_input",
        "target_core_id": "market_analyzer_v1",
        "target_child_cores": ["market_analyzer_v1"],
        "origin_surface": "market_analyzer_live",
    }


def case_01_runtime_bridge_reaches_retrieval_layer():
    result = run_external_memory_runtime_path(_strong_payload())

    assert result["status"] == "ok", f"unexpected runtime status: {result.get('status')}"
    assert result["qualification_decision"] == "persist_candidate", (
        f"unexpected qualification decision: {result.get('qualification_decision')}"
    )
    assert result["persistence_receipt"]["persistence_decision"] == "committed", (
        f"unexpected persistence decision: {result['persistence_receipt'].get('persistence_decision')}"
    )

    assert "external_memory_retrieval_result" in result, (
        f"missing external_memory_retrieval_result; keys={sorted(result.keys())}"
    )

    retrieval_result = result["external_memory_retrieval_result"]
    assert isinstance(retrieval_result, dict), (
        f"retrieval_result is not dict: {type(retrieval_result).__name__}"
    )


def case_02_runtime_bridge_does_not_emit_limit_shape_failure():
    result = run_external_memory_runtime_path(_strong_payload())
    retrieval_result = result.get("external_memory_retrieval_result")

    assert isinstance(retrieval_result, dict), (
        f"retrieval_result missing or invalid: {type(retrieval_result).__name__}"
    )

    receipt = retrieval_result.get("receipt", {})
    assert isinstance(receipt, dict), f"retrieval receipt invalid: {type(receipt).__name__}"

    assert receipt.get("failure_reason") != "invalid_limit", (
        f"failure_reason={receipt.get('failure_reason')} detail={receipt.get('detail')} "
        f"limit_field={receipt.get('limit')}"
    )
    assert receipt.get("detail") != "limit_not_integer", (
        f"failure_reason={receipt.get('failure_reason')} detail={receipt.get('detail')} "
        f"limit_field={receipt.get('limit')}"
    )


def case_03_runtime_bridge_preserves_integer_limit_input():
    result = run_external_memory_runtime_path(_strong_payload())
    retrieval_result = result.get("external_memory_retrieval_result")

    assert isinstance(retrieval_result, dict), (
        f"retrieval_result missing or invalid: {type(retrieval_result).__name__}"
    )

    receipt = retrieval_result.get("receipt", {})
    assert isinstance(receipt, dict), f"retrieval receipt invalid: {type(receipt).__name__}"

    bad_limit = receipt.get("limit")
    assert not isinstance(bad_limit, dict), (
        f"retrieval receipt shows dict-shaped limit field: {bad_limit}"
    )


def run():
    tests = [
        case_01_runtime_bridge_reaches_retrieval_layer,
        case_02_runtime_bridge_does_not_emit_limit_shape_failure,
        case_03_runtime_bridge_preserves_integer_limit_input,
    ]

    passed = 0
    failed = 0
    results = []

    for test in tests:
        try:
            test()
            passed += 1
            results.append({"case": test.__name__, "status": "passed"})
        except AssertionError as exc:
            failed += 1
            runtime_snapshot = None
            try:
                runtime_snapshot = run_external_memory_runtime_path(_strong_payload())
            except Exception as inner_exc:
                runtime_snapshot = {
                    "diagnostic_error": f"{inner_exc.__class__.__name__}: {inner_exc}",
                    "traceback": traceback.format_exc(),
                }

            results.append(
                {
                    "case": test.__name__,
                    "status": "failed",
                    "details": str(exc),
                    "runtime_snapshot": runtime_snapshot,
                }
            )
        except Exception as exc:
            failed += 1
            results.append(
                {
                    "case": test.__name__,
                    "status": "failed",
                    "details": f"{exc.__class__.__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )

    print(json.dumps({"passed": passed, "failed": failed, "results": results}, indent=2))
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
<<<<<<< HEAD
    run()
=======
    run()
>>>>>>> 38d503e (external memory pipeline fully activated: runtime → retrieval → promotion → pattern flow)
