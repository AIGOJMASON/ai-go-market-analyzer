from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.child_cores.contractor_builder_v1.ui.operator_dashboard_ui import operator_dashboard_page


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_page_renders() -> None:
    html = operator_dashboard_page()
    _assert(isinstance(html, str), "operator_dashboard_page should return html string")
    _assert(len(html) > 0, "html should not be empty")


def case_02_unified_sections_present() -> None:
    html = operator_dashboard_page()
    for section in ["System View", "Case", "Runtime", "Recommendation", "Cognition", "PM Workflow", "Governance"]:
        _assert(section in html, f"missing section heading: {section}")


def case_03_live_endpoint_referenced() -> None:
    html = operator_dashboard_page()
    _assert("/contractor-builder/run/live" in html, "live endpoint should be referenced")


def case_04_operator_input_controls_present() -> None:
    html = operator_dashboard_page()
    for control in ['id="request_id"', 'id="project_type"', 'id="trade_focus"', 'id="scope_summary"']:
        _assert(control in html, f"missing input control: {control}")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_page_renders", case_01_page_renders),
    ("case_02_unified_sections_present", case_02_unified_sections_present),
    ("case_03_live_endpoint_referenced", case_03_live_endpoint_referenced),
    ("case_04_operator_input_controls_present", case_04_operator_input_controls_present),
]


def run_probe() -> Dict[str, Any]:
    results: List[Dict[str, str]] = []
    passed = 0
    failed = 0

    for case_name, case_fn in TEST_CASES:
        try:
            case_fn()
            results.append({"case": case_name, "status": "passed"})
            passed += 1
        except Exception as exc:  # noqa: BLE001
            results.append({"case": case_name, "status": "failed", "error": str(exc)})
            failed += 1

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())