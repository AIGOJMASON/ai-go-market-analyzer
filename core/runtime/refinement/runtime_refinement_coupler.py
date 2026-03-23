"""
Stage 70 runtime refinement coupler.

This layer couples already-authorized engine allocation with engine-specific
runtime refinement receipts and routes each bounded channel forward.

It does not score, arbitrate, or reweight.
"""

from __future__ import annotations

from typing import Any, Dict

from .runtime_refinement_coupler_policy import (
    build_curved_mirror_channel,
    build_rosetta_channel,
    validate_allocation,
    validate_case_continuity,
    validate_curved_mirror_receipt,
    validate_rosetta_receipt,
)
from .runtime_refinement_coupler_registry import EMITTED_ARTIFACT_TYPE


def build_runtime_refinement_coupling_record(
    engine_allocation_record: Dict[str, Any],
    rosetta_refinement_receipt: Dict[str, Any],
    curved_mirror_refinement_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a sealed runtime_refinement_coupling_record.

    Inputs:
    - engine_allocation_record
    - rosetta_refinement_receipt
    - curved_mirror_refinement_receipt

    Output:
    - runtime_refinement_coupling_record
    """
    validate_allocation(engine_allocation_record)
    validate_rosetta_receipt(rosetta_refinement_receipt)
    validate_curved_mirror_receipt(curved_mirror_refinement_receipt)
    validate_case_continuity(
        engine_allocation_record,
        rosetta_refinement_receipt,
        curved_mirror_refinement_receipt,
    )

    rosetta_channel = build_rosetta_channel(
        engine_allocation_record,
        rosetta_refinement_receipt,
    )
    curved_mirror_channel = build_curved_mirror_channel(
        engine_allocation_record,
        curved_mirror_refinement_receipt,
    )

    return {
        "artifact_type": EMITTED_ARTIFACT_TYPE,
        "sealed": True,
        "case_id": engine_allocation_record["case_id"],
        "source_allocation_artifact_type": engine_allocation_record["artifact_type"],
        "source_rosetta_receipt_artifact_type": rosetta_refinement_receipt["artifact_type"],
        "source_curved_mirror_receipt_artifact_type": curved_mirror_refinement_receipt[
            "artifact_type"
        ],
        "allocation": {
            "rosetta_weight": float(engine_allocation_record["rosetta_weight"]),
            "curved_mirror_weight": float(engine_allocation_record["curved_mirror_weight"]),
        },
        "rosetta_channel": rosetta_channel,
        "curved_mirror_channel": curved_mirror_channel,
        "notes": (
            "Stage 70 couples runtime refinement with pre-authorized engine allocation "
            "without scoring, arbitration, or reweighting."
        ),
    }