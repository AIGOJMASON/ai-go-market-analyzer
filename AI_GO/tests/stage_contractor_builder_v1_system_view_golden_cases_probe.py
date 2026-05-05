from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.child_cores.contractor_builder_v1.api.schemas.contractor_builder_response import (
    build_contractor_builder_response,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_positive_package_recommendation() -> None:
    payload = {
        "status": "ok",
        "request_id": "golden-001",
        "route_mode": "pm_route_live",
        "input_mode": "live",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "governance_panel": {"watcher_passed": True},
        "case_panel": {"case_id": "golden-001", "title": "Interior kitchen refresh", "observed_at": None},
        "runtime_panel": {
            "project_class": "remodel",
            "trade_profile": "interior",
            "complexity_level": "medium",
            "location_mode": "remote",
            "scope_summary": "Interior kitchen refresh",
            "candidate_count": 1,
            "candidates": ["interior_package_v1"],
        },
        "recommendation_panel": {
            "recommendations": [
                {
                    "package_id": "interior_package_v1",
                    "title": "Interior Planning Package",
                    "rationale": "Aligned to remodel scope.",
                    "confidence": "medium",
                }
            ]
        },
        "refinement_panel": {
            "signal": "scope_alignment_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Scope and trade support package recommendation.",
            "narrative": "Advisory only.",
        },
    }
    response = build_contractor_builder_response(payload).model_dump(by_alias=True)
    _assert(response["system_view"]["recommendation"]["state"] == "present", "positive recommendation should be present")


def case_02_missing_confirmation_blocks_recommendation() -> None:
    payload = {
        "status": "ok",
        "request_id": "golden-002",
        "route_mode": "pm_route_live",
        "input_mode": "live",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "governance_panel": {"watcher_passed": True},
        "case_panel": {"case_id": "golden-002", "title": "Panel review only", "observed_at": None},
        "runtime_panel": {
            "project_class": "repair",
            "trade_profile": "electrical",
            "complexity_level": "low",
            "location_mode": "onsite",
            "scope_summary": "Panel review only",
            "candidate_count": 0,
            "candidates": [],
        },
        "recommendation_panel": {"recommendations": []},
        "rejection_panel": {"reason": "insufficient confirmation for package recommendation"},
        "refinement_panel": {
            "signal": "confirmation_gap_detected",
            "confidence_adjustment": "down",
            "risk_flag": "missing_confirmation",
            "insight": "Needs stronger confirmation.",
            "narrative": "Advisory only.",
        },
    }
    response = build_contractor_builder_response(payload).model_dump(by_alias=True)
    _assert(response["system_view"]["recommendation"]["state"] == "rejected", "missing confirmation should reject")
    _assert(response["system_view"]["cognition"]["refinement"]["risk_flag"] == "missing_confirmation", "risk flag mismatch")


def case_03_zero_pm_records_stable_shape() -> None:
    payload = {
        "status": "ok",
        "request_id": "golden-003",
        "route_mode": "pm_route",
        "input_mode": "fixture",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "governance_panel": {"watcher_passed": True},
        "case_panel": {"case_id": "golden-003", "title": "Fixture case", "observed_at": None},
        "runtime_panel": {
            "project_class": "remodel",
            "trade_profile": "general",
            "complexity_level": "medium",
            "location_mode": "remote",
            "scope_summary": "Fixture case",
            "candidate_count": 1,
            "candidates": ["general_package_v1"],
        },
        "recommendation_panel": {"recommendations": []},
        "refinement_panel": {
            "signal": "fixture_alignment",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Fixture case aligned.",
            "narrative": "Advisory only.",
        },
    }
    response = build_contractor_builder_response(payload).model_dump(by_alias=True)
    _assert(response["system_view"]["pm_workflow"]["state"] == "none", "pm_workflow should be none")
    _assert("governance" in response["system_view"], "governance missing")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_positive_package_recommendation", case_01_positive_package_recommendation),
    ("case_02_missing_confirmation_blocks_recommendation", case_02_missing_confirmation_blocks_recommendation),
    ("case_03_zero_pm_records_stable_shape", case_03_zero_pm_records_stable_shape),
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