from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.oracle.exposure_profile_runtime import (
    build_project_exposure_profile,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.oracle_receipt_builder import (
    build_oracle_receipt,
    write_oracle_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.procurement_advisory import (
    build_procurement_advisory,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.projection_engine import (
    build_oracle_projection,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.risk_radar_runtime import (
    build_risk_radar,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.shock_classifier import (
    classify_shock_record,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.snapshot_publisher import (
    publish_market_snapshot,
)


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not bool((execution_gate or {}).get("allowed") is True):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Oracle executor refused to run because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )


def execute_oracle_projection(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    project_id = str(payload.get("project_id", "")).strip()
    snapshot_id = str(payload.get("snapshot_id", "")).strip()
    exposure_profile_id = str(payload.get("exposure_profile_id", "")).strip()
    domain_exposure = payload.get("domain_exposure", {})

    if not isinstance(domain_exposure, dict):
        domain_exposure = {}

    snapshot = publish_market_snapshot(snapshot_id)

    shock = classify_shock_record(
        shock_id=f"shock-{project_id}-{snapshot_id}",
        snapshot=snapshot,
    )

    exposure_profile = build_project_exposure_profile(
        exposure_profile_id=exposure_profile_id,
        project_id=project_id,
        domain_exposure=domain_exposure,
    )

    projection = build_oracle_projection(
        projection_id=f"projection-{project_id}-{snapshot_id}",
        project_id=project_id,
        snapshot=snapshot,
        shock_record=shock,
        exposure_profile=exposure_profile,
    )

    radar = build_risk_radar(
        radar_id=f"radar-{project_id}",
        project_id=project_id,
        projections=[projection],
    )

    advisory = build_procurement_advisory(
        advisory_id=f"advisory-{project_id}-{snapshot['market_domain']}",
        project_id=project_id,
        projection=projection,
    )

    artifact_path = f"runtime://oracle/{project_id}/{snapshot_id}"

    receipt = build_oracle_receipt(
        event_type="create_projection",
        project_id=project_id,
        artifact_path=artifact_path,
        details={
            "snapshot_id": snapshot_id,
            "market_domain": snapshot["market_domain"],
            "exposure_profile_id": exposure_profile_id,
        },
    )

    receipt_path = write_oracle_receipt(receipt)

    return {
        "status": "completed",
        "project_id": project_id,
        "snapshot_id": snapshot_id,
        "artifact_path": artifact_path,
        "receipt_path": str(receipt_path),
        "snapshot": snapshot,
        "shock": shock,
        "exposure_profile": exposure_profile,
        "projection": projection,
        "risk_radar": radar,
        "procurement_advisory": advisory,
        "receipt": receipt,
    }