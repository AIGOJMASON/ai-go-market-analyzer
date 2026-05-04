from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.ui.operator_dashboard_ui import operator_dashboard_page


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_page_renders() -> None:
    html = operator_dashboard_page()
    _assert(isinstance(html, str), "operator_dashboard_page should return html string")
    _assert(len(html) > 0, "html should not be empty")


def case_02_single_surface_sections_present() -> None:
    html = operator_dashboard_page()

    required_strings = [
        "System View",
        "Case",
        "Runtime",
        "Recommendation",
        "Cognition",
        "PM Workflow",
        "Governance",
    ]
    for value in required_strings:
        _assert(value in html, f"missing section heading: {value}")


def case_03_live_endpoint_referenced() -> None:
    html = operator_dashboard_page()
    _assert("/market-analyzer/run/live" in html, "live run endpoint should be referenced")


def case_04_pm_workflow_not_split_into_separate_stage_pages() -> None:
    html = operator_dashboard_page()

    _assert("PM Workflow" in html, "PM Workflow section missing")
    _assert("Review Queue" not in html, "UI should not expose Review Queue as separate visible page heading")
    _assert("Planning Queue" not in html, "UI should not expose Planning Queue as separate visible page heading")
    _assert("Dispatch Record" not in html, "UI should not expose Dispatch Record as separate visible page heading")


def case_05_operator_input_controls_present() -> None:
    html = operator_dashboard_page()

    required_controls = [
        'id="request_id"',
        'id="symbol"',
        'id="sector"',
        'id="confirmation"',
        'id="price_change_pct"',
        'id="headline"',
    ]
    for control in required_controls:
        _assert(control in html, f"missing operator input control: {control}")


def case_06_system_view_fields_rendered_from_response() -> None:
    html = operator_dashboard_page()

    required_bindings = [
        'view.case || {}',
        'view.runtime || {}',
        'view.recommendation || {}',
        'view.cognition || {}',
        'view.pm_workflow || {}',
        'view.governance || {}',
    ]
    for binding in required_bindings:
        _assert(binding in html, f"missing system_view binding: {binding}")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_page_renders", case_01_page_renders),
    ("case_02_single_surface_sections_present", case_02_single_surface_sections_present),
    ("case_03_live_endpoint_referenced", case_03_live_endpoint_referenced),
    ("case_04_pm_workflow_not_split_into_separate_stage_pages", case_04_pm_workflow_not_split_into_separate_stage_pages),
    ("case_05_operator_input_controls_present", case_05_operator_input_controls_present),
    ("case_06_system_view_fields_rendered_from_response", case_06_system_view_fields_rendered_from_response),
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

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())