from __future__ import annotations

try:
    from api.event_classifier import classify_event
except ModuleNotFoundError:
    from AI_GO.api.event_classifier import classify_event


def run_probe():
    results = []

    supply_payload = {
        "request_id": "cls-001",
        "symbol": "COPX",
        "headline": "New Chile copper mine opening expands future supply outlook",
        "price_change_pct": 1.1,
        "sector": "materials",
        "confirmation": "partial",
    }
    supply_result = classify_event(supply_payload)
    results.append(
        {
            "case": "case_01_supply_keywords_classify_supply_expansion",
            "status": "passed"
            if supply_result["event_theme"] == "supply_expansion"
            and "keyword:chile" in supply_result["signals"]
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_lawful_exception_signal_replaces_non_necessity_for_supply_materials",
            "status": "passed"
            if "sector:lawful_exception" in supply_result["signals"]
            and "sector:non_necessity" not in supply_result["signals"]
            else "failed",
        }
    )

    geo_payload = {
        "request_id": "cls-002",
        "symbol": "XLE",
        "headline": "Oil jumps as regional conflict raises sanction fears",
        "price_change_pct": 2.0,
        "sector": "energy",
        "confirmation": "partial",
    }
    geo_result = classify_event(geo_payload)
    results.append(
        {
            "case": "case_03_geo_keywords_classify_geopolitical_shock",
            "status": "passed"
            if geo_result["event_theme"] == "geopolitical_shock"
            else "failed",
        }
    )

    energy_payload = {
        "request_id": "cls-003",
        "symbol": "XLE",
        "headline": "Energy stocks rebound after pressure eases",
        "price_change_pct": 2.4,
        "sector": "energy",
        "confirmation": "partial",
    }
    energy_result = classify_event(energy_payload)
    results.append(
        {
            "case": "case_04_energy_positive_classifies_energy_rebound",
            "status": "passed"
            if energy_result["event_theme"] == "energy_rebound"
            else "failed",
        }
    )

    confirm_payload = {
        "request_id": "cls-004",
        "symbol": "XLE",
        "headline": "Energy jumps early without confirmation",
        "price_change_pct": 1.7,
        "sector": "energy",
        "confirmation": "none",
    }
    confirm_result = classify_event(confirm_payload)
    results.append(
        {
            "case": "case_05_no_confirmation_classifies_confirmation_failure",
            "status": "passed"
            if confirm_result["event_theme"] == "confirmation_failure"
            and "confirmation:none" in confirm_result["signals"]
            else "failed",
        }
    )

    speculative_payload = {
        "request_id": "cls-005",
        "symbol": "XLY",
        "headline": "Retail momentum surges on speculative chatter",
        "price_change_pct": 3.5,
        "sector": "industrials",
        "confirmation": "partial",
    }
    speculative_result = classify_event(speculative_payload)
    results.append(
        {
            "case": "case_06_non_necessity_classifies_speculative_move",
            "status": "passed"
            if speculative_result["event_theme"] == "speculative_move"
            and "sector:non_necessity" in speculative_result["signals"]
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