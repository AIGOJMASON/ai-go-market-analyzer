from __future__ import annotations

from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.execution_gate import enforce_pre_execution_gate


def _good_packet() -> dict:
    return {
        "source_authority": "root_intelligence_spine",
        "target_child_core": "market_analyzer_v1",
        "spine_order": [
            "RESEARCH_CORE",
            "engines",
            "child_core_consumption_adapter",
            "child_core",
        ],
        "lineage": {
            "research_packet_id": "research-demo",
            "interpretation_packet_id": "engine-demo",
            "adapter_id": "market_analyzer_root_handoff_input",
        },
        "authority": {
            "execution_authority": False,
            "canon_authority": False,
            "governance_override": False,
            "watcher_override": False,
            "state_mutation_authority": False,
            "external_memory_write_authority": False,
            "raw_research_authority": False,
        },
        "external_source": True,
        "raw_input": False,
    }


def run_probe() -> dict:
    good = evaluate_cross_core_handoff(_good_packet())
    assert good["allowed"] is True
    assert good["status"] == "passed"

    missing_research = _good_packet()
    missing_research["spine_order"] = [
        "engines",
        "child_core_consumption_adapter",
        "child_core",
    ]
    missing_research["lineage"] = {
        "interpretation_packet_id": "engine-demo",
        "adapter_id": "market_analyzer_root_handoff_input",
    }

    missing_research_result = evaluate_cross_core_handoff(missing_research)
    assert missing_research_result["allowed"] is False

    raw_bypass = _good_packet()
    raw_bypass["raw_input"] = True
    raw_bypass["raw_external_input"] = True

    raw_bypass_result = evaluate_cross_core_handoff(raw_bypass)
    assert raw_bypass_result["allowed"] is False

    bad_authority = _good_packet()
    bad_authority["authority"]["execution_authority"] = True

    bad_authority_result = evaluate_cross_core_handoff(bad_authority)
    assert bad_authority_result["allowed"] is False

    gate_result = enforce_pre_execution_gate(
        {
            "governor_passed": True,
            "canon_passed": True,
            "watcher_passed": True,
            "research_lineage": True,
            "engine_processed": True,
            "adapter_applied": True,
            "external_source": True,
            "raw_input": False,
            "cross_core_packet": _good_packet(),
        }
    )

    assert gate_result["allowed"] is True
    assert gate_result["cross_core_enforcement"]["allowed"] is True

    return {
        "status": "passed",
        "phase": "Phase 5B.2",
        "good_packet_allowed": good["allowed"],
        "missing_research_blocked": missing_research_result["allowed"] is False,
        "raw_bypass_blocked": raw_bypass_result["allowed"] is False,
        "bad_authority_blocked": bad_authority_result["allowed"] is False,
        "pre_execution_gate_integrated": gate_result["allowed"] is True,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5B2_CROSS_CORE_ENFORCEMENT_PROBE: PASS")
    print(result)