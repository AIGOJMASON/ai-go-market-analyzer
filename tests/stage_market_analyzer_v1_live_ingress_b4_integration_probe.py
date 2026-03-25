from AI_GO.api.live_ingress import build_live_ingress_packet


def run_probe():
    payload = {
        "request_id": "live-b4-001",
        "symbol": "COPX",
        "headline": "Chile copper supply expansion lifts materials names on partial confirmation",
        "price_change_pct": 2.8,
        "sector": "materials",
        "confirmation": "partial",
    }

    packet = build_live_ingress_packet(payload)

    results = []

    results.append({
        "case": "case_01_packet_type_valid",
        "status": "passed" if packet["artifact_type"] == "live_ingress_packet" else "failed",
    })
    results.append({
        "case": "case_02_packet_is_sealed",
        "status": "passed" if packet["sealed"] is True else "failed",
    })
    results.append({
        "case": "case_03_historical_panel_present",
        "status": "passed" if "historical_analog_panel" in packet else "failed",
    })
    results.append({
        "case": "case_04_historical_panel_sealed",
        "status": "passed" if packet["historical_analog_panel"]["sealed"] is True else "failed",
    })
    results.append({
        "case": "case_05_event_theme_preserved",
        "status": "passed" if packet["historical_analog_panel"]["event_theme"] == packet["event_theme"] else "failed",
    })
    results.append({
        "case": "case_06_market_panel_carries_analog_confidence",
        "status": "passed" if packet["market_panel"]["historical_analog_confidence"] in {"low", "medium", "high"} else "failed",
    })
    results.append({
        "case": "case_07_market_panel_carries_analog_count",
        "status": "passed" if packet["market_panel"]["historical_analog_count"] >= 0 else "failed",
    })
    results.append({
        "case": "case_08_refinement_packet_annotates_analog_confidence",
        "status": "passed" if packet["refinement_packet"]["analog_confidence_band"] in {"low", "medium", "high"} else "failed",
    })
    results.append({
        "case": "case_09_candidate_panel_still_bounded",
        "status": "passed" if packet["candidate_panel"]["candidate_count"] in {0, 1} else "failed",
    })
    results.append({
        "case": "case_10_execution_still_blocked",
        "status": "passed" if packet["governance_panel"]["execution_allowed"] is False else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())