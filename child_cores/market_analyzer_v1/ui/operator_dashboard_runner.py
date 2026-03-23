from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .live_data_runner import run_live_case
from .operator_dashboard_builder import build_operator_dashboard
from .operator_dashboard_cli_report import render_operator_dashboard_cli


def run_operator_dashboard(case_id: Optional[str] = None) -> Dict[str, Any]:
    run_result = run_live_case(case_id=case_id)
    dashboard = build_operator_dashboard(run_result)
    return {
        "run_result": run_result,
        "dashboard": dashboard,
    }


if __name__ == "__main__":
    result = run_operator_dashboard()
    dashboard = result["dashboard"]
    print(render_operator_dashboard_cli(dashboard))
    print("--- JSON PAYLOAD ---")
    print(json.dumps(dashboard, indent=2))