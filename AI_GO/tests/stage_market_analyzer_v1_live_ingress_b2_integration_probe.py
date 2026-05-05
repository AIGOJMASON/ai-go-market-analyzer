from __future__ import annotations

try:
    from api.live_ingress import build_live_ingress_packet
except ModuleNotFoundError:
    from AI_GO.api.live_ingress import build_live_ingress_packet


def run_probe():
    results = []

    payload = {
        "request_id": "live-b2-001",
        "symbol": "COPX",
        "headline": "New Chile copper mine opening expands future supply outlook",
        "price_change_pct": 1.1,
        "sector": "materials",
        "confirmation": "partial",
    }

    packet = build_live_ingress_packet(payload)

    results.append(
        {
            "case": "case_01_packet_contains_classification_artifact",
            "status": "passed"
            if packet.get("classification", {}).get("artifact_type") == "event_classification"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_packet_market_panel_uses_classifier_event_theme",
            "status": "passed"
            if packet["market_panel"]["event_theme"] == packet["classification"]["event_theme"] == "supply_expansion"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_03_classifier_signals_are_visible",
            "status": "passed"
            if len(packet["classification"].get("signals", [])) > 0
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