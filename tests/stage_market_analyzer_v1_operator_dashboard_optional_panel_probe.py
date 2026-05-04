from __future__ import annotations

import sys
from pathlib import Path

# 🔷 FIX: add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import build_operator_dashboard


def main():
    passed = 0
    failed = 0
    results = []

    payload = {
        "status": "ok",
        "request_id": "builder-probe-001",
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "case_panel": {"case_id": "builder-probe-001", "title": "Probe case"},
        "market_panel": {"event_theme": "energy_rebound"},
        "runtime_panel": {"event_theme": "energy_rebound"},
        "recommendation_panel": {"recommendation_count": 1, "recommendations": [{"symbol": "XLE"}]},
        "governance_panel": {"watcher_passed": True, "approval_required": True},
        "refinement_panel": {"signal": "energy_rebound"},
        "rejection_panel": None,
        "external_memory_panel": None,
    }

    dashboard = build_operator_dashboard(payload)

    if "rejection_panel" not in dashboard and "external_memory_panel" not in dashboard:
        passed += 1
        results.append({"case": "case_01_none_optional_panels_omitted", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_01_none_optional_panels_omitted",
                "status": "failed",
                "detail": dashboard,
            }
        )

    payload_with_optional = {
        **payload,
        "rejection_panel": {"reason": "blocked"},
        "external_memory_panel": {"state": "present"},
    }
    dashboard = build_operator_dashboard(payload_with_optional)

    if (
        isinstance(dashboard.get("rejection_panel"), dict)
        and isinstance(dashboard.get("external_memory_panel"), dict)
    ):
        passed += 1
        results.append({"case": "case_02_dict_optional_panels_preserved", "status": "passed"})
    else:
        failed += 1
        results.append(
            {
                "case": "case_02_dict_optional_panels_preserved",
                "status": "failed",
                "detail": dashboard,
            }
        )

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()