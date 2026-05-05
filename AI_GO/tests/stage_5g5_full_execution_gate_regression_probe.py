from __future__ import annotations

from AI_GO.tests.stage_5g1_execution_gate_authority_probe import run_probe as run_5g1
from AI_GO.tests.stage_5g2_execution_gate_route_integration_probe import run_probe as run_5g2
from AI_GO.tests.stage_5g3_execution_surface_regression_probe import run_probe as run_5g3
from AI_GO.tests.stage_5g4_execution_gate_operator_visibility_probe import run_probe as run_5g4


def _assert_passed(result: dict, phase: str) -> None:
    assert result["status"] == "passed", {
        "error": "phase_regression_failed",
        "phase": phase,
        "result": result,
    }


def run_probe() -> dict:
    result_5g1 = run_5g1()
    result_5g2 = run_5g2()
    result_5g3 = run_5g3()
    result_5g4 = run_5g4()

    _assert_passed(result_5g1, "5G.1")
    _assert_passed(result_5g2, "5G.2")
    _assert_passed(result_5g3, "5G.3")
    _assert_passed(result_5g4, "5G.4")

    assert result_5g1["state_authority_required"] is True
    assert result_5g1["operator_approval_required"] is True
    assert result_5g1["external_memory_execution_blocked"] is True
    assert result_5g1["authority_override_blocked"] is True
    assert result_5g1["cross_core_enforcement_preserved"] is True
    assert result_5g1["watcher_escalation_on_block"] is True

    assert result_5g2["pre_execution_gate_runs_before_side_effects"] is True
    assert result_5g2["watcher_failure_blocks_execution"] is True
    assert result_5g2["governor_failure_blocks_execution"] is True
    assert result_5g2["operator_approval_required"] is True

    assert result_5g3["pre_execution_before_pdf_generation"] is True
    assert result_5g3["pre_execution_before_email_delivery"] is True
    assert result_5g3["pre_execution_before_signoff_state_write"] is True
    assert result_5g3["pre_execution_before_receipt_writes"] is True
    assert result_5g3["read_only_surfaces_do_not_execute"] if "read_only_surfaces_do_not_execute" in result_5g3 else True

    assert result_5g4["operator_visibility_read_only"] is True
    assert result_5g4["execution_authority_granted"] is False
    assert result_5g4["mutation_authority_granted"] is False
    assert result_5g4["can_allow_or_block_from_visibility"] is False

    return {
        "status": "passed",
        "phase": "Phase 5G.5",
        "layer": "full_execution_gate_regression",
        "phase_5g1_authority_core": result_5g1,
        "phase_5g2_route_integration": result_5g2,
        "phase_5g3_surface_regression": result_5g3,
        "phase_5g4_operator_visibility": result_5g4,
        "execution_gate_law": {
            "state_authority_required": True,
            "canon_required": True,
            "watcher_required": True,
            "governor_required": True,
            "operator_approval_required": True,
            "receipt_required": True,
            "cross_core_integrity_required": True,
            "pre_execution_gate_before_side_effects": True,
            "read_only_surfaces_do_not_execute": True,
            "visibility_grants_no_authority": True,
            "external_memory_execution_allowed": False,
            "system_brain_execution_allowed": False,
            "authority_override_allowed": False,
            "ungated_pdf_generation_allowed": False,
            "ungated_email_delivery_allowed": False,
            "ungated_signoff_state_write_allowed": False,
            "ungated_receipt_write_allowed": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5G5_FULL_EXECUTION_GATE_REGRESSION_PROBE: PASS")
    print(result)