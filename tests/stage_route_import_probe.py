from __future__ import annotations

import importlib
from typing import Dict, List


PROBE_NAME = "STAGE_ROUTE_IMPORT_PROBE"


ROUTE_MODULES = [
    # Core system
    "AI_GO.api.market_analyzer_api",
    "AI_GO.api.system_state_api",
    "AI_GO.api.canon_runtime_api",
    "AI_GO.api.ai_go_governance_explainer_api",

    # UI
    "AI_GO.ui.system_dashboard_ui",
    "AI_GO.api.contractor_dashboard_ui",

    # Contractor core routes
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


def run_probe() -> Dict:
    results: List[Dict] = []

    required_failed = []
    optional_failed = []

    for module_path in ROUTE_MODULES:
        try:
            module = importlib.import_module(module_path)

            router = getattr(module, "router", None)

            if router is None:
                results.append({
                    "status": "failed",
                    "module": module_path,
                    "error": "router_missing"
                })
                required_failed.append(module_path)
                continue

            results.append({
                "status": "ok",
                "module": module_path,
                "error": None
            })

        except Exception as e:
            results.append({
                "status": "failed",
                "module": module_path,
                "error": str(e)
            })
            required_failed.append(module_path)

    status = "passed" if not required_failed else "failed"

    return {
        "probe": PROBE_NAME,
        "status": status,
        "required_failed_count": len(required_failed),
        "optional_failed_count": len(optional_failed),
        "failed_required": required_failed,
        "failed_optional": optional_failed,
        "results": results,
    }


if __name__ == "__main__":
    output = run_probe()
    print(f"{PROBE_NAME}: {output['status'].upper()}")
    print("\nOUTPUT:\n", output)