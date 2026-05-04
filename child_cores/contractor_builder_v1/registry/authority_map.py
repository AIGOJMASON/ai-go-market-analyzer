"""
Authority map for contractor_builder_v1.

This file is the canonical authority boundary declaration for the contractor family.
It records what each module is allowed to do, what it must not do, and how authority
is split across structured truth, controlled mutation, advisory intelligence,
projection, and orchestration.
"""

from __future__ import annotations

from typing import Any, Dict, List


CONTRACTOR_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "project_intake": {
        "authority_class": "structured_truth",
        "allowed": [
            "create_project_profile",
            "lock_initial_baselines",
            "record_project_identity",
            "write_intake_receipts",
        ],
        "prohibited": [
            "mutate_existing_project_history_destructively",
            "approve_project_changes",
            "release_external_reports",
        ],
    },
    "workflow": {
        "authority_class": "structured_truth",
        "allowed": [
            "generate_phase_structures",
            "store_phase_expectations",
            "track_expected_vs_actual_timing",
            "record_client_signoff_events",
            "surface_drift_advisories",
        ],
        "prohibited": [
            "autonomous_schedule_mutation",
            "autonomous_phase_approval",
            "autonomous_contract_mutation",
            "legal_determinations",
        ],
    },
    "change": {
        "authority_class": "controlled_mutation",
        "allowed": [
            "create_change_packets",
            "compute_cost_delta",
            "compute_dead_time_cost",
            "compute_schedule_delta",
            "collect_signatures",
            "seal_amendment_records",
            "write_change_receipts",
        ],
        "prohibited": [
            "autonomous_scope_mutation_without_approval",
            "autonomous_schedule_mutation",
            "legal_determinations",
            "auto_distribution_to_owners_or_clients",
        ],
    },
    "decision_log": {
        "authority_class": "structured_truth",
        "allowed": [
            "create_internal_decision_records",
            "record_context_locks",
            "record_declared_impacts",
            "collect_dual_acknowledgment",
            "write_decision_receipts",
        ],
        "prohibited": [
            "external_owner_visibility_by_default",
            "destructive_revision_of_approved_records",
            "contract_mutation",
        ],
    },
    "risk_register": {
        "authority_class": "structured_truth",
        "allowed": [
            "create_risk_records",
            "record_human_probability_and_impact_labels",
            "track_weekly_reviews",
            "log_status_changes",
            "write_risk_receipts",
        ],
        "prohibited": [
            "automated_numeric_risk_scoring",
            "autonomous_mitigation_execution",
            "contract_mutation",
        ],
    },
    "assumption_log": {
        "authority_class": "structured_truth",
        "allowed": [
            "create_assumption_records",
            "track_validation_status",
            "record_invalidation",
            "route_invalidation_to_lawful_conversion_paths",
            "write_assumption_receipts",
        ],
        "prohibited": [
            "deletion_of_assumptions",
            "silent_assumption_invalidation",
            "autonomous_impact_determination_without_record",
        ],
    },
    "comply": {
        "authority_class": "structured_truth",
        "allowed": [
            "lock_compliance_snapshot",
            "track_permits",
            "record_inspection_events",
            "perform_governed_code_lookup",
            "write_compliance_receipts",
        ],
        "prohibited": [
            "legal_determinations",
            "auto_migrate_project_snapshots",
            "rewrite_inspection_history",
        ],
    },
    "router": {
        "authority_class": "advisory_intelligence",
        "allowed": [
            "store_schedule_blocks",
            "detect_overlaps",
            "detect_dependency_violations",
            "detect_capacity_conflicts",
            "label_cascade_risk",
            "write_router_receipts",
        ],
        "prohibited": [
            "autonomous_schedule_mutation",
            "autonomous_crew_assignment",
            "labor_management_execution",
        ],
    },
    "oracle": {
        "authority_class": "advisory_intelligence",
        "allowed": [
            "publish_market_snapshots",
            "classify_shocks",
            "store_exposure_profiles",
            "generate_advisory_projections",
            "generate_risk_flags",
            "generate_procurement_advisory",
            "write_oracle_receipts",
        ],
        "prohibited": [
            "direct_project_state_mutation",
            "direct_schedule_mutation",
            "direct_budget_mutation",
            "auto_procurement_execution",
        ],
    },
    "report": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "build_numbers_first_reports",
            "generate_summary_drafts_from_structured_fields",
            "collect_pm_approvals",
            "archive_approved_reports",
            "write_report_receipts",
        ],
        "prohibited": [
            "invent_new_numbers_in_summary",
            "speculative_narrative_without_structured_support",
            "auto_release",
        ],
    },
    "weekly_cycle": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "collect_agent_snapshots",
            "trigger_project_report_builds",
            "stage_reports_for_pm_review",
            "aggregate_approved_portfolio_views",
            "write_weekly_cycle_receipts",
        ],
        "prohibited": [
            "mutate_underlying_module_truth",
            "approve_reports",
            "release_reports_automatically",
        ],
    },
    "projection": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "assemble_operator_payloads",
            "shape_project_views",
            "shape_portfolio_views",
            "persist_latest_payload_state",
        ],
        "prohibited": [
            "truth_mutation",
            "approval_logic_execution",
            "schedule_or_scope_mutation",
        ],
    },
    "explanation": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "render_bounded_operator_explanations",
            "interpret_weekly_reports_in_plain_language",
        ],
        "prohibited": [
            "invent_numbers",
            "override_structured_truth",
            "mutate_runtime_state",
        ],
    },
    "ui": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "build_dashboard_runtime_structures",
            "render_read_only_operator_views",
        ],
        "prohibited": [
            "mutate_project_truth",
            "approve_changes",
            "approve_reports",
        ],
    },
    "adapters": {
        "authority_class": "projection_and_orchestration",
        "allowed": [
            "translate_module_outputs_thinly",
            "preserve_reference_integrity",
            "route_lawful_module_fields_between_surfaces",
        ],
        "prohibited": [
            "deep_business_logic_duplication",
            "authority_reassignment",
            "cross_module_hidden_mutation",
        ],
    },
}


AUTHORITY_CLASS_ORDER: List[str] = [
    "structured_truth",
    "controlled_mutation",
    "advisory_intelligence",
    "projection_and_orchestration",
]


def get_contractor_authority_map() -> Dict[str, Dict[str, Any]]:
    """
    Return a defensive shallow copy of the contractor authority map.
    """
    return {key: dict(value) for key, value in CONTRACTOR_AUTHORITY_MAP.items()}


def get_modules_for_authority_class(authority_class: str) -> List[str]:
    """
    Return all module IDs that belong to the requested authority class.
    """
    return [
        module_id
        for module_id, metadata in CONTRACTOR_AUTHORITY_MAP.items()
        if metadata.get("authority_class") == authority_class
    ]


def is_action_allowed(module_id: str, action: str) -> bool:
    """
    Check whether a declared action is explicitly allowed for a module.
    """
    module = CONTRACTOR_AUTHORITY_MAP.get(module_id, {})
    return action in module.get("allowed", [])


def is_action_prohibited(module_id: str, action: str) -> bool:
    """
    Check whether a declared action is explicitly prohibited for a module.
    """
    module = CONTRACTOR_AUTHORITY_MAP.get(module_id, {})
    return action in module.get("prohibited", [])