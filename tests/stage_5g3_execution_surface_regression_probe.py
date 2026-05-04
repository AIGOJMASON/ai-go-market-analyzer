from __future__ import annotations

import importlib
import inspect
from typing import Any, Dict, List


EXECUTION_SURFACE_REGRESSION_VERSION = "v5G.3"

SIDE_EFFECT_TOKENS = [
    "build_phase_closeout_pdf(",
    "send_email(",
    "append_client_signoff_status(",
    "write_delivery_receipt(",
    "write_pdf_receipt(",
    "write_workflow_receipt(",
    "write_project_receipt_copy(",
    "_persist_pdf_artifact_record(",
    "_persist_email_record(",
]

READ_ONLY_FORBIDDEN_TOKENS = [
    "send_email(",
    "append_client_signoff_status(",
    "build_phase_closeout_pdf(",
    "write_delivery_receipt(",
    "write_pdf_receipt(",
    "write_workflow_receipt(",
    "write_project_receipt_copy(",
    "enforce_pre_execution_gate(",
]


def _module_source(module_name: str) -> str:
    module = importlib.import_module(module_name)
    return inspect.getsource(module)


def _function_source(module_name: str, function_name: str) -> str:
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return inspect.getsource(function)


def _index_or_fail(source: str, token: str) -> int:
    index = source.find(token)
    if index < 0:
        raise AssertionError(f"Missing required token: {token}")
    return index


def _assert_not_present(source: str, tokens: List[str]) -> None:
    present = [token for token in tokens if token in source]
    if present:
        raise AssertionError(
            {
                "error": "forbidden_tokens_present",
                "tokens": present,
            }
        )


def test_phase_closeout_route_uses_pre_execution_gate() -> None:
    module_source = _module_source("AI_GO.api.contractor_phase_closeout_api")

    assert "from AI_GO.core.execution_gate import enforce_pre_execution_gate" in module_source
    assert "build_phase_closeout_pre_execution_context" in module_source
    assert "def _enforce_phase_closeout_pre_execution(" in module_source
    assert "return enforce_pre_execution_gate(pre_execution_context)" in module_source


def test_phase_closeout_pre_execution_runs_before_side_effects() -> None:
    source = _function_source(
        "AI_GO.api.contractor_phase_closeout_api",
        "run_phase_closeout",
    )

    pre_execution_index = _index_or_fail(source, "_enforce_phase_closeout_pre_execution(")

    side_effect_positions: Dict[str, int] = {}

    for token in SIDE_EFFECT_TOKENS:
        index = source.find(token)
        if index >= 0:
            side_effect_positions[token] = index
            assert pre_execution_index < index, {
                "error": "side_effect_before_pre_execution_gate",
                "token": token,
                "pre_execution_index": pre_execution_index,
                "side_effect_index": index,
            }

    required_side_effects = [
        "build_phase_closeout_pdf(",
        "send_email(",
        "append_client_signoff_status(",
        "write_delivery_receipt(",
        "write_pdf_receipt(",
        "write_workflow_receipt(",
    ]

    for token in required_side_effects:
        assert token in side_effect_positions, f"Expected phase closeout side effect missing: {token}"


def test_phase_closeout_returns_pre_execution_decision() -> None:
    source = _function_source(
        "AI_GO.api.contractor_phase_closeout_api",
        "run_phase_closeout",
    )

    assert '"mode": "governed_execution"' in source
    assert '"pre_execution_decision": pre_execution_decision' in source
    assert '"governance_decision": governance_decision' in source
    assert '"watcher_result": watcher_result' in source


def test_system_watcher_surface_is_read_only() -> None:
    source = _module_source("AI_GO.api.contractor_system_watcher_api")

    assert "watch_contractor_system" in source
    assert "@router.post" in source
    _assert_not_present(source, READ_ONLY_FORBIDDEN_TOKENS)


def test_contractor_builder_router_is_mount_only_or_health_only() -> None:
    source = _module_source("AI_GO.api.contractor_builder_api")

    assert "include_router" in source
    assert "def contractor_builder_health" in source
    assert '"execution_allowed": False' in source
    assert '"approval_required": True' in source

    _assert_not_present(
        source,
        [
            "send_email(",
            "append_client_signoff_status(",
            "build_phase_closeout_pdf(",
            "write_delivery_receipt(",
            "write_pdf_receipt(",
            "write_workflow_receipt(",
        ],
    )


def test_canon_runtime_surface_is_enforcement_only() -> None:
    source = _module_source("AI_GO.api.canon_runtime_api")

    assert "enforce_canon_action" in source or "enforce_canon_action_from_dict" in source
    assert "build_canon_index" in source
    assert "validate_canon_runtime" in source

    _assert_not_present(source, READ_ONLY_FORBIDDEN_TOKENS)


def test_execution_gate_package_exports_final_gate() -> None:
    module = importlib.import_module("AI_GO.core.execution_gate")

    assert hasattr(module, "evaluate_execution_gate")
    assert hasattr(module, "enforce_pre_execution_gate")


def run_probe() -> dict:
    test_phase_closeout_route_uses_pre_execution_gate()
    test_phase_closeout_pre_execution_runs_before_side_effects()
    test_phase_closeout_returns_pre_execution_decision()
    test_system_watcher_surface_is_read_only()
    test_contractor_builder_router_is_mount_only_or_health_only()
    test_canon_runtime_surface_is_enforcement_only()
    test_execution_gate_package_exports_final_gate()

    return {
        "status": "passed",
        "phase": "Phase 5G.3",
        "layer": "execution_gate_surface_regression",
        "phase_closeout_route_guarded": True,
        "pre_execution_before_pdf_generation": True,
        "pre_execution_before_email_delivery": True,
        "pre_execution_before_signoff_state_write": True,
        "pre_execution_before_receipt_writes": True,
        "system_watcher_classified_read_only": True,
        "contractor_builder_router_mount_only": True,
        "canon_runtime_classified_enforcement_only": True,
        "execution_gate_exports_available": True,
        "execution_surface_law": {
            "all_known_execution_surfaces_guarded": True,
            "read_only_surfaces_do_not_execute": True,
            "side_effects_must_follow_pre_execution_gate": True,
            "ungated_pdf_generation_allowed": False,
            "ungated_email_delivery_allowed": False,
            "ungated_signoff_state_write_allowed": False,
            "ungated_receipt_write_allowed": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5G3_EXECUTION_SURFACE_REGRESSION_PROBE: PASS")
    print(result)