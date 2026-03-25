from __future__ import annotations

from api.live_ingress import build_live_ingress_packet


def run_probe():
    results = []

    energy_payload = {
        "request_id": "live-raw-001",
        "symbol": "XLE",
        "headline": "Energy stocks rebound after supply disruption fears ease",
        "price_change_pct": 2.4,
        "sector": "energy",
        "confirmation": "partial",
    }
    energy_packet = build_live_ingress_packet(energy_payload)

    results.append(
        {
            "case": "case_01_energy_payload_normalizes_to_live_ingress_packet",
            "status": "passed"
            if energy_packet["artifact_type"] == "live_ingress_packet"
            and energy_packet["market_panel"]["event_theme"] == "energy_rebound"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_energy_payload_creates_recommendation_seed",
            "status": "passed"
            if energy_packet["recommendation_seed"]["allowed"] is True
            and energy_packet["recommendation_seed"]["recommendation_count"] == 1
            else "failed",
        }
    )

    supply_payload = {
        "request_id": "live-raw-002",
        "symbol": "COPX",
        "headline": "New Chile copper mine opening expands future supply outlook",
        "price_change_pct": 1.1,
        "sector": "materials",
        "confirmation": "partial",
    }
    supply_packet = build_live_ingress_packet(supply_payload)

    results.append(
        {
            "case": "case_03_supply_payload_classifies_to_supply_expansion",
            "status": "passed"
            if supply_packet["market_panel"]["event_theme"] == "supply_expansion"
            else "failed",
        }
    )

    rejection_payload = {
        "request_id": "live-raw-003",
        "symbol": "XLY",
        "headline": "Speculative retail rebound surges on momentum chatter",
        "price_change_pct": 3.8,
        "sector": "industrials",
        "confirmation": "partial",
    }
    rejection_packet = build_live_ingress_packet(rejection_payload)

    results.append(
        {
            "case": "case_04_non_necessity_payload_rejects_recommendation",
            "status": "passed"
            if rejection_packet["rejection_panel"]["rejected"] is True
            and rejection_packet["recommendation_seed"]["allowed"] is False
            else "failed",
        }
    )

    no_confirm_payload = {
        "request_id": "live-raw-004",
        "symbol": "XLE",
        "headline": "Energy jumps early without confirmation",
        "price_change_pct": 1.7,
        "sector": "energy",
        "confirmation": "none",
    }
    no_confirm_packet = build_live_ingress_packet(no_confirm_payload)

    results.append(
        {
            "case": "case_05_no_confirmation_payload_routes_to_confirmation_failure",
            "status": "passed"
            if no_confirm_packet["market_panel"]["event_theme"] == "confirmation_failure"
            and no_confirm_packet["rejection_panel"]["rejected"] is True
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