"""
Module registry for contractor_builder_v1.

This file declares each contractor family module, its authority posture, dependency
shape, and runtime status. It is the canonical inventory surface for module-level
activation and implementation order.
"""

from __future__ import annotations

from typing import Any, Dict, List


CONTRACTOR_MODULE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "registry": {
        "module_id": "registry",
        "status": "active",
        "authority_level": "declarative",
        "implementation_phase": 0,
        "depends_on": [],
        "purpose": "Declares family identity, module inventory, and authority mapping.",
    },
    "governance": {
        "module_id": "governance",
        "status": "active",
        "authority_level": "declarative_and_policy",
        "implementation_phase": 0,
        "depends_on": ["registry"],
        "purpose": "Defines shared identity, integrity, receipt, append-only, and reference law.",
    },
    "project_intake": {
        "module_id": "project_intake",
        "status": "planned",
        "authority_level": "controlled_record_creation",
        "implementation_phase": 0,
        "depends_on": ["registry", "governance"],
        "purpose": "Creates contractor projects and baseline locks.",
    },
    "workflow": {
        "module_id": "workflow",
        "status": "planned",
        "authority_level": "advisory_only",
        "implementation_phase": 1,
        "depends_on": ["project_intake", "governance"],
        "purpose": "Defines phases, timing, expectations, signoffs, and phase history.",
    },
    "change": {
        "module_id": "change",
        "status": "planned",
        "authority_level": "controlled_mutation_with_receipt",
        "implementation_phase": 2,
        "depends_on": ["workflow", "governance"],
        "purpose": "Governs rebids, amendments, dead time, pricing deltas, and approvals.",
    },
    "decision_log": {
        "module_id": "decision_log",
        "status": "planned",
        "authority_level": "record_and_advisory",
        "implementation_phase": 3,
        "depends_on": ["change", "workflow", "governance"],
        "purpose": "Records internal-only context-locked decisions with dual acknowledgment.",
    },
    "risk_register": {
        "module_id": "risk_register",
        "status": "planned",
        "authority_level": "advisory_record_only",
        "implementation_phase": 3,
        "depends_on": ["decision_log", "change", "governance"],
        "purpose": "Tracks operational risks under human judgment-first doctrine.",
    },
    "assumption_log": {
        "module_id": "assumption_log",
        "status": "planned",
        "authority_level": "record_and_advisory",
        "implementation_phase": 3,
        "depends_on": ["decision_log", "change", "risk_register", "governance"],
        "purpose": "Tracks project assumptions and forces conversion when invalidated.",
    },
    "comply": {
        "module_id": "comply",
        "status": "planned",
        "authority_level": "advisory_with_controlled_record_logging",
        "implementation_phase": 4,
        "depends_on": ["workflow", "governance"],
        "purpose": "Locks jurisdiction snapshots and records permits, inspections, and lookups.",
    },
    "router": {
        "module_id": "router",
        "status": "planned",
        "authority_level": "advisory_only",
        "implementation_phase": 5,
        "depends_on": ["workflow", "governance"],
        "purpose": "Detects schedule conflicts, overlaps, capacity issues, and cascade risk.",
    },
    "oracle": {
        "module_id": "oracle",
        "status": "planned",
        "authority_level": "advisory_only",
        "implementation_phase": 6,
        "depends_on": ["governance", "project_intake"],
        "purpose": "Adds external market, shock, projection, and procurement advisory overlays.",
    },
    "report": {
        "module_id": "report",
        "status": "planned",
        "authority_level": "read_only_orchestrator_with_pm_gated_release",
        "implementation_phase": 7,
        "depends_on": [
            "workflow",
            "change",
            "comply",
            "router",
            "oracle",
            "decision_log",
            "risk_register",
            "assumption_log",
            "governance",
        ],
        "purpose": "Builds numbers-first weekly project and portfolio reports with PM approval.",
    },
    "weekly_cycle": {
        "module_id": "weekly_cycle",
        "status": "planned",
        "authority_level": "read_only_orchestrator",
        "implementation_phase": 8,
        "depends_on": [
            "report",
            "workflow",
            "change",
            "comply",
            "router",
            "oracle",
            "decision_log",
            "risk_register",
            "assumption_log",
            "governance",
        ],
        "purpose": "Runs weekly scans, collects module snapshots, and stages reports for PM review.",
    },
    "projection": {
        "module_id": "projection",
        "status": "planned",
        "authority_level": "read_only_projection",
        "implementation_phase": 9,
        "depends_on": ["report", "weekly_cycle", "governance"],
        "purpose": "Assembles contractor operator payloads for dashboards and views.",
    },
    "explanation": {
        "module_id": "explanation",
        "status": "planned",
        "authority_level": "bounded_explanation",
        "implementation_phase": 9,
        "depends_on": ["projection", "report"],
        "purpose": "Converts structured truths into operator-readable language without inventing facts.",
    },
    "ui": {
        "module_id": "ui",
        "status": "planned",
        "authority_level": "read_only_surface_runtime",
        "implementation_phase": 9,
        "depends_on": ["projection", "explanation"],
        "purpose": "Shapes dashboard payloads and powers contractor operator surfaces.",
    },
    "adapters": {
        "module_id": "adapters",
        "status": "planned",
        "authority_level": "thin_adapter_only",
        "implementation_phase": 9,
        "depends_on": [
            "workflow",
            "change",
            "comply",
            "router",
            "oracle",
            "decision_log",
            "risk_register",
            "assumption_log",
            "report",
        ],
        "purpose": "Provides thin lawful translation between module outputs without deep entanglement.",
    },
}


def get_contractor_module_registry() -> Dict[str, Dict[str, Any]]:
    """
    Return a defensive shallow copy of the module registry.
    """
    return {key: dict(value) for key, value in CONTRACTOR_MODULE_REGISTRY.items()}


def get_modules_for_phase(phase_id: int) -> List[str]:
    """
    Return module IDs scheduled for a given implementation phase.
    """
    return [
        module_id
        for module_id, metadata in CONTRACTOR_MODULE_REGISTRY.items()
        if metadata.get("implementation_phase") == phase_id
    ]


def get_active_or_planned_modules() -> List[str]:
    """
    Return all module IDs that are not retired.
    """
    return [
        module_id
        for module_id, metadata in CONTRACTOR_MODULE_REGISTRY.items()
        if metadata.get("status") in {"active", "planned"}
    ]