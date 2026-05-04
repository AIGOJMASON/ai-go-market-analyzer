from __future__ import annotations

import copy
import json

from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_context,
    build_pm_coupling_packet,
    extract_target_context,
)
from AI_GO.core.watcher.cross_core_enforcement import (
    assert_cross_core_allowed,
    enforce_cross_core_chain,
)


def _governed_result(source_id: str) -> dict:
    return {
        "mode": "governed_execution",
        "status": "created",
        "entry": {
            "status": "created",
        },
        "artifact_path": f"AI_GO/state/contractor_builder_v1/projects/by_project/project-6c/{source_id}.json",
        "receipt_path": f"AI_GO/receipts/contractor_builder_v1/{source_id}.json",
        "state": {
            "valid": True,
        },
        "watcher": {
            "valid": True,
        },
        "execution_gate": {
            "allowed": True,
        },
        "mutation_guard": {
            "valid": True,
        },
        "result_summary": {
            "artifact_type": "post_execution_result_summary",
            "effect": "execution_completed",
            "counts": {
                "state_mutations": 1,
                "artifacts_created": 1,
            },
        },
    }


def _build_valid_context() -> dict:
    project_id = "project-6c-cross-core-coupling"
    phase_id = "phase-6c-cross-core-coupling"

    packets = [
        build_pm_coupling_packet(
            project_id=project_id,
            phase_id=phase_id,
            actor="stage_6c_cross_core_coupling_enforcement_probe",
            source_service="oracle",
            target_service="decision",
            source_result=_governed_result("oracle"),
            influence_summary="Oracle pressure must inform decision context.",
        ),
        build_pm_coupling_packet(
            project_id=project_id,
            phase_id=phase_id,
            actor="stage_6c_cross_core_coupling_enforcement_probe",
            source_service="decision",
            target_service="risk",
            source_result=_governed_result("decision"),
            influence_summary="Decision declared impact must inform risk context.",
        ),
        build_pm_coupling_packet(
            project_id=project_id,
            phase_id=phase_id,
            actor="stage_6c_cross_core_coupling_enforcement_probe",
            source_service="risk",
            target_service="router",
            source_result=_governed_result("risk"),
            influence_summary="Risk posture must inform router context.",
        ),
        build_pm_coupling_packet(
            project_id=project_id,
            phase_id=phase_id,
            actor="stage_6c_cross_core_coupling_enforcement_probe",
            source_service="router",
            target_service="comply",
            source_result=_governed_result("router"),
            influence_summary="Router pressure must inform compliance context.",
        ),
    ]

    return build_pm_coupling_context(
        project_id=project_id,
        phase_id=phase_id,
        actor="stage_6c_cross_core_coupling_enforcement_probe",
        packets=packets,
    )


def run_probe() -> dict:
    valid_context = _build_valid_context()

    allowed_decision = enforce_cross_core_chain(
        payload=valid_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    assert allowed_decision["artifact_type"] == "cross_core_enforcement_decision"
    assert allowed_decision["artifact_version"] == "v6c.1"
    assert allowed_decision["allowed"] is True
    assert allowed_decision["blocked"] is False
    assert allowed_decision["status"] == "allowed"
    assert allowed_decision["decision"] == "allow"
    assert allowed_decision["chain"]["link_count"] == 4
    assert allowed_decision["authority"]["may_execute"] is False
    assert allowed_decision["authority"]["may_mutate_state"] is False
    assert allowed_decision["sealed"] is True

    assert_cross_core_allowed(
        payload=valid_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    risk_target_context = extract_target_context(
        coupling_context=valid_context,
        target_service="risk",
    )

    assert risk_target_context["target_service"] == "risk"
    assert risk_target_context["packet_count"] == 1
    assert risk_target_context["authority"]["execution_allowed"] is False
    assert risk_target_context["authority"]["mutation_allowed"] is False

    illegal_context = copy.deepcopy(valid_context)
    illegal_packet = copy.deepcopy(illegal_context["packets"][0])
    illegal_packet["packet_id"] = "illegal-router-to-decision"
    illegal_packet["source"]["source_type"] = "router"
    illegal_packet["target"]["target_service"] = "decision"
    illegal_context["packets"].append(illegal_packet)

    illegal_decision = enforce_cross_core_chain(
        payload=illegal_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    assert illegal_decision["allowed"] is False
    assert illegal_decision["blocked"] is True
    illegal_codes = {reason["code"] for reason in illegal_decision["reasons"]}
    assert "illegal_cross_core_path" in illegal_codes

    ungoverned_context = copy.deepcopy(valid_context)
    ungoverned_context["packets"][0]["source"]["governance_refs"]["watcher_valid"] = False

    ungoverned_decision = enforce_cross_core_chain(
        payload=ungoverned_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    assert ungoverned_decision["allowed"] is False
    assert ungoverned_decision["blocked"] is True
    ungoverned_codes = {reason["code"] for reason in ungoverned_decision["reasons"]}
    assert "cross_core_packet_not_governed" in ungoverned_codes

    out_of_order_context = build_pm_coupling_context(
        project_id="project-6c-cross-core-coupling",
        phase_id="phase-6c-cross-core-coupling",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
        packets=[
            valid_context["packets"][2],
            valid_context["packets"][0],
        ],
    )

    out_of_order_decision = enforce_cross_core_chain(
        payload=out_of_order_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    assert out_of_order_decision["allowed"] is False
    assert out_of_order_decision["blocked"] is True
    order_codes = {reason["code"] for reason in out_of_order_decision["reasons"]}
    assert "cross_core_chain_order_violation" in order_codes

    duplicate_context = copy.deepcopy(valid_context)
    duplicate_context["packets"].append(copy.deepcopy(valid_context["packets"][0]))

    duplicate_decision = enforce_cross_core_chain(
        payload=duplicate_context,
        action="phase_6c_cross_core_coupling_validate",
        profile="contractor_builder_v1",
        actor="stage_6c_cross_core_coupling_enforcement_probe",
    )

    assert duplicate_decision["allowed"] is False
    assert duplicate_decision["blocked"] is True
    duplicate_codes = {reason["code"] for reason in duplicate_decision["reasons"]}
    assert "duplicate_cross_core_packet" in duplicate_codes

    return {
        "status": "passed",
        "phase": "6C.1",
        "link": "cross_core_coupling_enforcement",
        "allowed_decision": allowed_decision,
        "risk_target_context": risk_target_context,
        "illegal_decision": illegal_decision,
        "ungoverned_decision": ungoverned_decision,
        "out_of_order_decision": out_of_order_decision,
        "duplicate_decision": duplicate_decision,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_6C_CROSS_CORE_COUPLING_ENFORCEMENT_PROBE: PASS")
    print(json.dumps(output, indent=2))