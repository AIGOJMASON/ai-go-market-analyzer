from __future__ import annotations

try:
    from api.live_ingress import build_live_ingress_packet
except ModuleNotFoundError:
    from AI_GO.api.live_ingress import build_live_ingress_packet


def run_probe():
    results = []

    payload = {
        "request_id": "live-b3-001",
        "symbol": "COPX",
        "headline": "New Chile copper mine opening expands future supply outlook",
        "price_change_pct": 1.1,
        "sector": "materials",
        "confirmation": "partial",
    }

    packet = build_live_ingress_packet(payload)

    results.append(
        {
            "case": "case_01_live_ingress_contains_signal_stack",
            "status": "passed"
            if packet.get("signal_stack", {}).get("artifact_type") == "signal_stack_record"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_signal_stack_event_theme_matches_classification",
            "status": "passed"
            if packet["signal_stack"]["event_theme"] == packet["classification"]["event_theme"] == "supply_expansion"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_03_signal_stack_contains_confirmation_and_legality",
            "status": "passed"
            if "confirmation:partial" in packet["signal_stack"]["stack_signals"]
            and "legality:lawful_exception" in packet["signal_stack"]["stack_signals"]
            else "failed",
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