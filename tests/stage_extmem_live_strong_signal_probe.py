# tests/stage_extmem_live_strong_signal_probe.py

from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
        run_market_analyzer_external_memory_path,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.runtime_path import (
        run_market_analyzer_external_memory_path,
    )


def main():
    passed = 0
    failed = 0
    results = []

    request_id = f"extmem-live-strong-{uuid.uuid4().hex[:8]}"

    result = run_market_analyzer_external_memory_path(
        request_id=request_id,
        symbol="XLE",
        headline="Energy disruption event",
        price_change_pct=2.0,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_rebound",
        macro_bias="supportive",
        route_mode="pm_route",
        source_type="live_market_input",
    )

    qualification_record = result.get("qualification_record", {})
    persistence_receipt = result.get("persistence_receipt", {})
    retrieval_result = result.get("external_memory_retrieval_result", {})
    retrieval_artifact = result.get("external_memory_retrieval_artifact", {})
    retrieval_receipt = result.get("external_memory_retrieval_receipt", {})

    if qualification_record.get("decision") == "persist_candidate":
        passed += 1
        results.append({"case": "case_01_strong_signal_qualifies_for_persistence", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_01_strong_signal_qualifies_for_persistence",
                "status": "failed",
                "detail": qualification_record,
            }
        )

    if persistence_receipt.get("persistence_decision") == "committed":
        passed += 1
        results.append({"case": "case_02_strong_signal_commits_to_memory", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_02_strong_signal_commits_to_memory",
                "status": "failed",
                "detail": persistence_receipt,
            }
        )

    retrieval_present = isinstance(retrieval_result, dict) and (
        isinstance(retrieval_artifact, dict) or isinstance(retrieval_receipt, dict)
    )
    if retrieval_present:
        passed += 1
        results.append({"case": "case_03_strong_signal_reaches_retrieval_surface", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_03_strong_signal_reaches_retrieval_surface",
                "status": "failed",
                "detail": {
                    "external_memory_retrieval_result": retrieval_result,
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