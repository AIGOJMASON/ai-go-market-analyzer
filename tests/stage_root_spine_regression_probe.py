from __future__ import annotations

import importlib
import traceback
from typing import Dict, List

REQUIRED_ROUTES = [
    # Core
    "AI_GO.api.market_analyzer_api",

    # Optional system (still should resolve if present)
    "AI_GO.api.system_state_api",
    "AI_GO.api.canon_runtime_api",
    "AI_GO.api.ai_go_governance_explainer_api",

    # UI
    "AI_GO.ui.system_dashboard_ui",
    "AI_GO.api.contractor_dashboard_ui",

    # Contractor REQUIRED (Northstar critical)
    "AI_GO.api.contractor_projects_api",
    "AI_GO.api.contractor_intake_api",
    "AI_GO.api.contractor_project_record_api",
    "AI_GO.api.contractor_workflow_api",
    "AI_GO.api.contractor_change_api",
    "AI_GO.api.contractor_change_signoff_api",
    "AI_GO.api.contractor_decision_api",
    "AI_GO.api.contractor_risk_api",
    "AI_GO.api.contractor_comply_api",
    "AI_GO.api.contractor_router_api",
    "AI_GO.api.contractor_oracle_api",
    "AI_GO.api.contractor_report_api",
    "AI_GO.api.contractor_weekly_cycle_api",
    "AI_GO.api.contractor_phase_closeout_api",
]

OPTIONAL_ROUTES = [
    # Add anything you truly consider optional here
]


def try_import(module_name: str) -> Dict:
    try:
        importlib.import_module(module_name)
        return {
            "status": "ok",
            "module": module_name,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "failed",
            "module": module_name,
            "error": str(e),
            "trace": traceback.format_exc(),
        }


def run_probe() -> Dict:
    results: List[Dict] = []
    failed_required: List[Dict] = []
    failed_optional: List[Dict] = []

    print("\n=== STAGE ROOT SPINE REGRESSION PROBE ===\n")

    for route in REQUIRED_ROUTES:
        result = try_import(route)

        if result["status"] == "ok":
            print(f"[ROUTER OK] {route}")
        else:
            print(f"[ROUTER FAIL] {route}")
            print(f"  → {result['error']}")
            failed_required.append(result)

        results.append(result)

    for route in OPTIONAL_ROUTES:
        result = try_import(route)

        if result["status"] == "ok":
            print(f"[ROUTER OK OPTIONAL] {route}")
        else:
            print(f"[ROUTER FAIL OPTIONAL] {route}")
            failed_optional.append(result)

        results.append(result)

    passed = len(failed_required) == 0

    print("\n=== SUMMARY ===")
    print(f"Required routes failed: {len(failed_required)}")
    print(f"Optional routes failed: {len(failed_optional)}")

    if passed:
        print("\n✅ STAGE_ROOT_SPINE_REGRESSION_PROBE: PASS")
    else:
        print("\n❌ STAGE_ROOT_SPINE_REGRESSION_PROBE: FAIL")

    return {
        "status": "passed" if passed else "failed",
        "required_failed_count": len(failed_required),
        "optional_failed_count": len(failed_optional),
        "failed_required": failed_required,
        "failed_optional": failed_optional,
        "all_results": results,
    }


if __name__ == "__main__":
    output = run_probe()
    print("\nOUTPUT:\n", output)