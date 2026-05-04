"""
Family registry for contractor_builder_v1.

This file declares the contractor builder child-core family as a governed AI_GO
surface and records the top-level family identity, posture, and module inventory.
"""

from __future__ import annotations

from typing import Any, Dict, List


CONTRACTOR_BUILDER_REGISTRY: Dict[str, Any] = {
    "child_core_id": "contractor_builder_v1",
    "family_name": "CONTRACTOR_BUILDER_v1",
    "status": "phase_0_registry_frozen",
    "system_family": "AI_GO child core family",
    "description": (
        "Governed contractor and construction operations child-core family with "
        "authority-bounded modules for project intake, workflow, change governance, "
        "decision logging, compliance, routing, reporting, and weekly orchestration."
    ),
    "root_posture": {
        "governed": True,
        "auditable": True,
        "append_only_required_in_declared_modules": True,
        "pm_gated_release": True,
        "numbers_first_then_summary": True,
        "autonomous_scope_mutation_allowed": False,
        "autonomous_schedule_mutation_allowed": False,
        "legal_determinations_allowed": False,
        "auto_release_allowed": False,
    },
    "canonical_phases": [
        {
            "phase_id": 0,
            "phase_name": "family_root_and_governance_freeze",
            "status": "active",
        },
        {
            "phase_id": 1,
            "phase_name": "workflow_backbone",
            "status": "planned",
        },
        {
            "phase_id": 2,
            "phase_name": "controlled_mutation_backbone",
            "status": "planned",
        },
        {
            "phase_id": 3,
            "phase_name": "internal_accountability_branch",
            "status": "planned",
        },
        {
            "phase_id": 4,
            "phase_name": "compliance_branch",
            "status": "planned",
        },
        {
            "phase_id": 5,
            "phase_name": "routing_and_conflict_branch",
            "status": "planned",
        },
        {
            "phase_id": 6,
            "phase_name": "oracle_external_pressure_branch",
            "status": "planned",
        },
        {
            "phase_id": 7,
            "phase_name": "report_surface",
            "status": "planned",
        },
        {
            "phase_id": 8,
            "phase_name": "weekly_orchestration",
            "status": "planned",
        },
        {
            "phase_id": 9,
            "phase_name": "projection_explanation_ui_and_api_surfaces",
            "status": "planned",
        },
    ],
    "module_order": [
        "registry",
        "governance",
        "project_intake",
        "workflow",
        "change",
        "decision_log",
        "risk_register",
        "assumption_log",
        "comply",
        "router",
        "oracle",
        "report",
        "weekly_cycle",
        "projection",
        "explanation",
        "ui",
        "adapters",
    ],
    "authority_zones": {
        "structured_truth": [
            "project_intake",
            "workflow",
            "decision_log",
            "risk_register",
            "assumption_log",
            "comply",
        ],
        "controlled_mutation": [
            "change",
        ],
        "advisory_intelligence": [
            "router",
            "oracle",
        ],
        "projection_and_orchestration": [
            "report",
            "weekly_cycle",
            "projection",
            "explanation",
            "ui",
            "adapters",
        ],
    },
    "required_top_level_state_root": "AI_GO/state/contractor_builder_v1/",
    "required_top_level_receipts_root": "AI_GO/receipts/contractor_builder_v1/",
    "required_api_router": "AI_GO/api/contractor_builder_api.py",
    "required_tests_prefix": "AI_GO/tests/stage_contractor_",
}


def get_contractor_builder_registry() -> Dict[str, Any]:
    """
    Return a defensive shallow copy of the contractor family registry.
    """
    return dict(CONTRACTOR_BUILDER_REGISTRY)


def get_contractor_module_order() -> List[str]:
    """
    Return the canonical module order for contractor_builder_v1.
    """
    return list(CONTRACTOR_BUILDER_REGISTRY["module_order"])