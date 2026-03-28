from __future__ import annotations

import json

from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import (
    run_live_payload,
)


def run():
    payload = {
        "case_id": "TEST-STRONG-001",
        "request_id": "TEST-STRONG-001",
        "headline": "Confirmed major oil infrastructure disruption impacting supply chains globally",
        "symbol": "XLE",
        "sector": "energy",
        "price_change_pct": 3.5,
        "confirmation": "confirmed",
        "observed_at": None,
        "macro_context": {
            "headline": "Confirmed major oil infrastructure disruption impacting supply chains globally",
            "macro_bias": "supportive",
        },
        "event_signal": {
            "event_theme": "energy_rebound",
            "confirmed": True,
            "propagation": "fast",
        },
        "candidates": [
            {
                "symbol": "XLE",
                "sector": "energy",
                "necessity_qualified": True,
                "rebound_confirmed": True,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": "high",
            }
        ],
        "operator_notes": "Strong live probe case for external memory retrieval and promotion.",
    }

    result = run_live_payload(payload)

    summary = {
        "has_runtime": "external_memory_runtime_result" in result,
        "has_retrieval": result.get("external_memory_retrieval_artifact") is not None,
        "has_promotion": result.get("external_memory_promotion_artifact") is not None,
    }

    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))

    print("\n=== FULL RESULT ===")
    print(json.dumps(result, indent=2))

    return summary


if __name__ == "__main__":
    run()
