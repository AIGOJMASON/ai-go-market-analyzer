from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from AI_GO.core.execution_gate import evaluate_execution_gate, enforce_pre_execution_gate
from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


def _build_research_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "research_core_packet",
        "artifact_version": "v5G.1_probe",
        "packet_id": "research-demo",
        "research_packet_id": "research-demo",
        "request_id": "stage-5g1-research-demo",
        "source_authority": "RESEARCH_CORE",
        "origin_authority": "RESEARCH_CORE",
        "trust": {"trust_class": "verified", "pre_weight": 0.8},
        "screening": {
            "status": "passed",
            "valid": True,
            "allowed": True,
            "trust_class": "verified",
            "pre_weight": 0.8,
        },
        "source_screening": {
            "status": "passed",
            "valid": True,
            "allowed": True,
            "trust_class": "verified",
            "pre_weight": 0.8,
        },
        "routing": {
            "primary_child_core": "market_analyzer_v1",
            "child_core_targets": ["market_analyzer_v1"],
        },
        "research_input": {
            "request_id": "stage-5g1-research-demo",
            "provider": "stage_5g1_probe",
            "provider_kind": "manual_probe",
            "symbol": "XLE",
            "title": "Verified energy signal",
            "headline": "Verified energy signal",
            "summary": "Synthetic governed research packet for 5G.1 execution gate probe.",
            "signal_type": "market_signal",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
            "source_refs": ["manual_probe:stage_5g1_probe"],
            "child_core_targets": ["market_analyzer_v1"],
        },
        "payload": {
            "request_id": "stage-5g1-research-demo",
            "provider": "stage_5g1_probe",
            "provider_kind": "manual_probe",
            "symbol": "XLE",
            "title": "Verified energy signal",
            "headline": "Verified energy signal",
            "summary": "Synthetic governed research packet for 5G.1 execution gate probe.",
            "signal_type": "market_signal",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
            "source_refs": ["manual_probe:stage_5g1_probe"],
            "child_core_targets": ["market_analyzer_v1"],
        },
        "bounded": True,
        "sealed": True,
    }


def _good_cross_core_packet() -> Dict[str, Any]:
    handoff = curate_research_packet_for_child_cores(
        research_packet=_build_research_packet()
    )

    cross_core = evaluate_cross_core_handoff(handoff)
    if cross_core.get("allowed") is not True:
        raise AssertionError(
            {
                "error": "generated_cross_core_packet_invalid",
                "cross_core": cross_core,
                "handoff": handoff,
            }
        )

    return handoff


def _good_execution_context() -> Dict[str, Any]:
    return {
        "request_id": "stage-5g1-demo",
        "route": "/contractor-builder/phase-closeout/run",
        "method": "POST",
        "actor": "test_operator",
        "target": "contractor_builder_v1.phase_closeout",
        "child_core_id": "contractor_builder_v1",
        "action_type": "phase_closeout",
        "action_class": "workflow_transition",
        "execution_intent": True,
        "project_id": "project-demo",
        "phase_id": "phase-demo-inspection",
        "governor_passed": True,
        "watcher_passed": True,
        "state_passed": True,
        "canon_passed": True,
        "operator_approved": True,
        "receipt_planned": True,
        "state_mutation_declared": True,
        "raw_input": False,
        "external_source": False,
        "lineage": {
            "research_packet_id": "research-demo",
            "interpretation_packet_id": "engine-demo",
            "adapter_id": "adapter-demo",
        },
        "root_spine": {
            "spine_order": [
                "RESEARCH_CORE",
                "engines",
                "child_core_consumption_adapter",
                "child_core",
            ],
        },
        "authority": {
            "ai_execution_authority": False,
            "memory_execution_authority": False,
            "system_brain_execution_authority": False,
            "watcher_override": False,
            "state_authority_override": False,
            "canon_override": False,
            "execution_gate_override": False,
            "governance_override": False,
            "bypass_execution_gate": False,
            "hidden_state_mutation": False,
        },
        "cross_core_packet": _good_cross_core_packet(),
    }


def test_execution_gate_allows_only_fully_governed_context() -> None:
    decision = evaluate_execution_gate(_good_execution_context())
    assert decision["allowed"] is True
    assert decision["status"] == "passed"


def test_execution_gate_blocks_without_state_authority() -> None:
    context = _good_execution_context()
    context["state_passed"] = False

    decision = evaluate_execution_gate(context)
    assert decision["allowed"] is False
    assert "state_authority_required" in decision["failed_checks"]


def test_execution_gate_blocks_without_operator_approval() -> None:
    context = _good_execution_context()
    context["operator_approved"] = False

    decision = evaluate_execution_gate(context)
    assert decision["allowed"] is False
    assert "operator_approval_required" in decision["failed_checks"]


def test_execution_gate_blocks_external_memory_execution_source() -> None:
    context = _good_execution_context()
    context["source_type"] = "external_memory"

    decision = evaluate_execution_gate(context)
    assert decision["allowed"] is False
    assert "source_not_forbidden" in decision["failed_checks"]


def test_execution_gate_blocks_forbidden_authority_claim() -> None:
    context = _good_execution_context()
    context["authority"]["canon_override"] = True

    decision = evaluate_execution_gate(context)
    assert decision["allowed"] is False
    assert "no_forbidden_authority_claims" in decision["failed_checks"]


def test_pre_execution_gate_passes_with_cross_core_enforcement() -> None:
    decision = enforce_pre_execution_gate(_good_execution_context())

    assert decision["allowed"] is True
    assert decision["status"] == "passed"
    assert decision["execution_gate"]["allowed"] is True
    assert decision["cross_core_enforcement"]["allowed"] is True


def test_pre_execution_gate_blocks_and_escalates_to_watcher() -> None:
    context = _good_execution_context()
    context["raw_input"] = True

    try:
        enforce_pre_execution_gate(context)
    except PermissionError as exc:
        payload = exc.args[0]
    else:
        raise AssertionError("Expected pre-execution gate to block raw input.")

    assert payload["error"] == "pre_execution_gate_blocked"
    assert payload["decision"]["allowed"] is False
    assert payload["watcher_violation"]["artifact_type"] == "enforcement_violation_record"


def test_pre_execution_gate_blocks_invalid_cross_core_packet() -> None:
    context = _good_execution_context()

    bad_packet = deepcopy(context["cross_core_packet"])
    bad_packet["bounded"] = False
    context["cross_core_packet"] = bad_packet

    try:
        enforce_pre_execution_gate(context)
    except PermissionError as exc:
        payload = exc.args[0]
    else:
        raise AssertionError("Expected pre-execution gate to block invalid cross-core packet.")

    assert payload["error"] == "pre_execution_gate_blocked"
    assert payload["decision"]["allowed"] is False
    assert payload["decision"]["cross_core_enforcement"]["allowed"] is False


def run_probe() -> dict:
    test_execution_gate_allows_only_fully_governed_context()
    test_execution_gate_blocks_without_state_authority()
    test_execution_gate_blocks_without_operator_approval()
    test_execution_gate_blocks_external_memory_execution_source()
    test_execution_gate_blocks_forbidden_authority_claim()
    test_pre_execution_gate_passes_with_cross_core_enforcement()
    test_pre_execution_gate_blocks_and_escalates_to_watcher()
    test_pre_execution_gate_blocks_invalid_cross_core_packet()

    return {
        "status": "passed",
        "phase": "Phase 5G.1",
        "layer": "execution_gate_authority_core",
        "fully_governed_context_allowed": True,
        "state_authority_required": True,
        "operator_approval_required": True,
        "external_memory_execution_blocked": True,
        "authority_override_blocked": True,
        "cross_core_enforcement_preserved": True,
        "real_5c_engine_handoff_required": True,
        "invalid_cross_core_packet_blocked": True,
        "watcher_escalation_on_block": True,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5G1_EXECUTION_GATE_AUTHORITY_PROBE: PASS")
    print(result)