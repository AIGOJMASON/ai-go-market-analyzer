from __future__ import annotations

import copy
import json

from AI_GO.core.watcher.cross_core_enforcement import (
    assert_cross_core_allowed,
    enforce_cross_core_chain,
)


def _packet(
    *,
    packet_id: str,
    source: str,
    target: str,
) -> dict:
    packet = {
        "artifact_type": "contractor_pm_coupling_packet",
        "artifact_version": "v1.0",
        "packet_id": packet_id,
        "created_at": "2026-04-30T00:00:00+00:00",
        "child_core_id": "contractor_builder_v1",
        "issuing_layer": "PM_CORE",
        "actor": "PM_CORE",
        "project_id": "project-cross-core-enforcement-probe",
        "phase_id": "phase-cross-core-enforcement-probe",
        "source": {
            "source_type": source,
            "source_id": f"{source}-source-id",
            "source_status": "created",
            "source_hash": f"{source}-source-hash",
            "result_summary_hash": f"{source}-result-summary-hash",
            "receipt_refs": [
                f"AI_GO/receipts/contractor_builder_v1/{source}/receipt.json"
            ],
            "governance_refs": {
                "governance_packet_id": (
                    f"governance-contractor_{source}-{source}_create"
                ),
                "watcher_valid": True,
                "state_valid": True,
                "execution_gate_allowed": True,
                "result_effect": "execution_completed",
                "result_summary_hash": f"{source}-result-summary-hash",
            },
        },
        "target": {
            "target_service": target,
            "target_child_core_id": "contractor_builder_v1",
            "allowed_use": "bounded_context_only",
        },
        "influence": {
            "influence_type": f"{source}_to_{target}",
            "summary": "Probe packet.",
        },
        "authority": {
            "pm_owned": True,
            "downstream_execution_allowed": False,
            "downstream_mutation_allowed": False,
            "grants_authority": False,
            "requires_downstream_governance": True,
            "requires_downstream_watcher": True,
            "requires_downstream_execution_gate": True,
        },
        "constraints": {
            "no_lateral_service_call": True,
            "no_direct_state_mutation": True,
            "no_direct_external_action": True,
            "lineage_required": True,
            "packet_remains_context_not_truth": True,
        },
        "sealed": True,
        "notes": "",
        "packet_hash": f"{packet_id}-hash",
    }
    return packet


def _valid_payload() -> dict:
    return {
        "packets": [
            _packet(
                packet_id="packet-oracle-decision",
                source="oracle",
                target="decision",
            ),
            _packet(
                packet_id="packet-decision-risk",
                source="decision",
                target="risk",
            ),
            _packet(
                packet_id="packet-risk-router",
                source="risk",
                target="router",
            ),
            _packet(
                packet_id="packet-assumption-decision",
                source="assumption",
                target="decision",
            ),
        ]
    }


def run_probe() -> dict:
    valid_payload = _valid_payload()

    allowed_decision = enforce_cross_core_chain(
        payload=valid_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert allowed_decision["artifact_type"] == "cross_core_enforcement_decision"
    assert allowed_decision["allowed"] is True
    assert allowed_decision["blocked"] is False
    assert allowed_decision["status"] == "allowed"
    assert allowed_decision["decision"] == "allow"
    assert allowed_decision["chain"]["link_count"] == 4
    assert allowed_decision["authority"]["may_block_propagation"] is True
    assert allowed_decision["authority"]["may_execute"] is False
    assert allowed_decision["authority"]["may_mutate_state"] is False
    assert allowed_decision["authority"]["may_call_services"] is False
    assert allowed_decision["constraints"]["invalid_chain_blocks"] is True
    assert allowed_decision["sealed"] is True

    assert_cross_core_allowed(
        payload=valid_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    illegal_path_payload = _valid_payload()
    illegal_path_payload["packets"].append(
        _packet(
            packet_id="packet-router-decision-illegal",
            source="router",
            target="decision",
        )
    )

    illegal_path_decision = enforce_cross_core_chain(
        payload=illegal_path_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert illegal_path_decision["allowed"] is False
    assert illegal_path_decision["blocked"] is True
    illegal_codes = {reason["code"] for reason in illegal_path_decision["reasons"]}
    assert "illegal_cross_core_path" in illegal_codes

    ungoverned_payload = _valid_payload()
    ungoverned_payload["packets"][0]["source"]["governance_refs"][
        "watcher_valid"
    ] = False

    ungoverned_decision = enforce_cross_core_chain(
        payload=ungoverned_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert ungoverned_decision["allowed"] is False
    assert ungoverned_decision["blocked"] is True
    ungoverned_codes = {
        reason["code"] for reason in ungoverned_decision["reasons"]
    }
    assert "cross_core_packet_not_governed" in ungoverned_codes

    out_of_order_payload = {
        "packets": [
            _packet(
                packet_id="packet-risk-router-first",
                source="risk",
                target="router",
            ),
            _packet(
                packet_id="packet-oracle-decision-second",
                source="oracle",
                target="decision",
            ),
        ]
    }

    out_of_order_decision = enforce_cross_core_chain(
        payload=out_of_order_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert out_of_order_decision["allowed"] is False
    assert out_of_order_decision["blocked"] is True
    order_codes = {reason["code"] for reason in out_of_order_decision["reasons"]}
    assert "cross_core_chain_order_violation" in order_codes

    duplicate_payload = _valid_payload()
    duplicate_payload["packets"].append(copy.deepcopy(duplicate_payload["packets"][0]))

    duplicate_decision = enforce_cross_core_chain(
        payload=duplicate_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert duplicate_decision["allowed"] is False
    assert duplicate_decision["blocked"] is True
    duplicate_codes = {reason["code"] for reason in duplicate_decision["reasons"]}
    assert "duplicate_cross_core_packet" in duplicate_codes

    missing_payload = {"packets": []}

    missing_decision = enforce_cross_core_chain(
        payload=missing_payload,
        action="cross_core_chain_validate",
        profile="contractor_builder_v1",
        actor="stage_contractor_cross_core_enforcement_probe",
    )

    assert missing_decision["allowed"] is False
    assert missing_decision["blocked"] is True
    missing_codes = {reason["code"] for reason in missing_decision["reasons"]}
    assert "cross_core_packets_missing" in missing_codes

    return {
        "status": "passed",
        "phase": "3.5",
        "link": "cross_core_enforcement",
        "allowed_decision": allowed_decision,
        "illegal_path_decision": illegal_path_decision,
        "ungoverned_decision": ungoverned_decision,
        "out_of_order_decision": out_of_order_decision,
        "duplicate_decision": duplicate_decision,
        "missing_decision": missing_decision,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_CROSS_CORE_ENFORCEMENT_PROBE: PASS")
    print(json.dumps(output, indent=2))