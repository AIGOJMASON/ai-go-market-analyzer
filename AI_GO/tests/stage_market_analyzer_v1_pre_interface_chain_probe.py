# AI_GO/tests/stage_market_analyzer_v1_pre_interface_chain_probe.py

from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner import finalize_operator_dashboard_payload


def _valid_payload():
    return {
        "status": "ok",
        "request_id": "probe-003",
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "case_panel": {"case_id": "probe-003", "title": "Probe case"},
        "market_panel": {"event_theme": "energy_rebound"},
        "governance_panel": {"watcher_passed": True, "approval_required": True},
        "recommendation_panel": {"count": 1, "items": [{"symbol": "XLE"}]},
        "refinement_panel": {"signal": "pattern_detected"},
        "external_memory_panel": {"promotion_status": "promoted"},
        "pm_workflow_panel": {"dispatch_class": "review"},
    }


def main():
    passed = 0
    failed = 0
    results = []

    payload = finalize_operator_dashboard_payload(
        base_payload=_valid_payload(),
        upstream_refs={"output_merge_receipt_id": "omr_001"},
        persist_receipts=False,
    )
    if "pre_interface_watcher" in payload and "pre_interface_smi" in payload:
        passed += 1
        results.append({"case": "case_01_valid_chain_attaches_final_layers", "status": "passed"})
    else:
        failed += 1
        results.append({"case": "case_01_valid_chain_attaches_final_layers", "status": "failed", "detail": payload})

    broken = _valid_payload()
    broken["execution_allowed"] = True
    payload = finalize_operator_dashboard_payload(
        base_payload=broken,
        upstream_refs={"output_merge_receipt_id": "omr_002"},
        persist_receipts=False,
    )
    if payload.get("status") == "rejected" and "pre_interface_watcher" in payload:
        passed += 1
        results.append({"case": "case_02_invalid_chain_rejects_before_interface", "status": "passed"})
    else:
        failed += 1
        results.append({"case": "case_02_invalid_chain_rejects_before_interface", "status": "failed", "detail": payload})

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()