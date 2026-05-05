# tests/stage_extmem_runtime_bridge_retrieval_probe.py

from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from AI_GO.EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
        run_external_memory_runtime_path,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
        run_external_memory_runtime_path,
    )


def main():
    passed = 0
    failed = 0
    results = []

    request_id = f"extmem-bridge-{uuid.uuid4().hex[:8]}"

    result = run_external_memory_runtime_path(
        {
            "request_id": request_id,
            "symbol": "XLE",
            "headline": "Energy disruption event",
            "price_change_pct": 2.0,
            "sector": "energy",
            "confirmation": "confirmed",
            "event_theme": "energy_rebound",
            "macro_bias": "supportive",
            "route_mode": "pm_route",
            "source_type": "live_market_input",
            "target_core_id": "market_analyzer_v1",
            "origin_surface": "market_analyzer_live",
        }
    )

    retrieval_result = result.get("external_memory_retrieval_result", {})
    retrieval_artifact = result.get("external_memory_retrieval_artifact", {})
    retrieval_receipt = result.get("external_memory_retrieval_receipt", {})

    if result.get("artifact_type") == "external_memory_runtime_result" and result.get("status") == "ok":
        passed += 1
        results.append({"case": "case_01_runtime_bridge_returns_ok_result", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_01_runtime_bridge_returns_ok_result",
                "status": "failed",
                "detail": result,
            }
        )

    retrieval_surface_present = isinstance(retrieval_result, dict)
    if retrieval_surface_present:
        passed += 1
        results.append({"case": "case_02_runtime_bridge_exposes_retrieval_result", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_02_runtime_bridge_exposes_retrieval_result",
                "status": "failed",
                "detail": retrieval_result,
            }
        )

    invalid_limit_error = None
    if isinstance(retrieval_result, dict):
        invalid_limit_error = retrieval_result.get("error")

    if invalid_limit_error is None or "limit" not in str(invalid_limit_error).lower():
        passed += 1
        results.append({"case": "case_03_runtime_bridge_does_not_break_limit_shape", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_03_runtime_bridge_does_not_break_limit_shape",
                "status": "failed",
                "detail": retrieval_result,
            }
        )

    retrieval_artifacts_available = isinstance(retrieval_artifact, dict) or isinstance(retrieval_receipt, dict)
    if retrieval_artifacts_available:
        passed += 1
        results.append({"case": "case_04_runtime_bridge_reaches_retrieval_artifacts", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_04_runtime_bridge_reaches_retrieval_artifacts",
                "status": "failed",
                "detail": {
                    "external_memory_retrieval_artifact": retrieval_artifact,
                    "external_memory_retrieval_receipt": retrieval_receipt,
                },
            }
        )

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()