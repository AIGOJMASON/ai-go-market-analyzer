from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.receipts.receipt_writer import enrich_receipt


PROBE_NAME = "STAGE_RECEIPT_PAYLOAD_PROBE"


REQUIRED_TOP_LEVEL = [
    "receipt_id",
    "module_name",
    "event_type",
    "classification",
    "authority_metadata",
    "integrity",
]

REQUIRED_CLASSIFICATION = [
    "mutation_class",
    "persistence_type",
    "execution_allowed",
    "state_mutation_allowed",
    "workflow_mutation_allowed",
    "project_truth_mutation_allowed",
    "authority_mutation_allowed",
    "governed_persistence",
]

REQUIRED_AUTHORITY = [
    "authority_id",
    "operation",
    "actor",
    "source",
    "module_name",
    "event_type",
    "can_execute",
    "can_mutate_runtime",
    "can_mutate_workflow_state",
    "can_mutate_project_truth",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "immutable_record",
    "governed_persistence",
]


def _missing(payload: Dict[str, Any], fields: List[str]) -> List[str]:
    return [field for field in fields if field not in payload]


def _check_bool_false(payload: Dict[str, Any], fields: List[str]) -> List[str]:
    return [field for field in fields if payload.get(field) is not False]


def _check_bool_true(payload: Dict[str, Any], fields: List[str]) -> List[str]:
    return [field for field in fields if payload.get(field) is not True]


def _check_receipt(label: str, receipt: Dict[str, Any]) -> Dict[str, Any]:
    missing_top = _missing(receipt, REQUIRED_TOP_LEVEL)

    classification = receipt.get("classification")
    authority = receipt.get("authority_metadata")

    if not isinstance(classification, dict):
        classification = {}

    if not isinstance(authority, dict):
        authority = {}

    missing_classification = _missing(classification, REQUIRED_CLASSIFICATION)
    missing_authority = _missing(authority, REQUIRED_AUTHORITY)

    unsafe_classification_flags = _check_bool_false(
        classification,
        [
            "execution_allowed",
            "state_mutation_allowed",
            "workflow_mutation_allowed",
            "project_truth_mutation_allowed",
            "authority_mutation_allowed",
        ],
    )

    unsafe_authority_flags = _check_bool_false(
        authority,
        [
            "can_execute",
            "can_mutate_runtime",
            "can_mutate_workflow_state",
            "can_mutate_project_truth",
            "can_override_governance",
            "can_override_watcher",
            "can_override_execution_gate",
        ],
    )

    missing_true_flags = _check_bool_true(
        authority,
        [
            "immutable_record",
            "governed_persistence",
        ],
    )

    passed = not any(
        [
            missing_top,
            missing_classification,
            missing_authority,
            unsafe_classification_flags,
            unsafe_authority_flags,
            missing_true_flags,
        ]
    )

    return {
        "label": label,
        "status": "ok" if passed else "failed",
        "missing_top_level": missing_top,
        "missing_classification": missing_classification,
        "missing_authority_metadata": missing_authority,
        "unsafe_classification_flags": unsafe_classification_flags,
        "unsafe_authority_flags": unsafe_authority_flags,
        "missing_true_authority_flags": missing_true_flags,
        "receipt_id": receipt.get("receipt_id"),
        "module_name": receipt.get("module_name"),
        "event_type": receipt.get("event_type"),
    }


def run_probe() -> Dict[str, Any]:
    sample_receipts = [
        enrich_receipt(
            receipt={
                "project_id": "project-receipt-payload-probe",
                "artifact_path": "runtime://receipt-payload-probe/decision",
                "details": {"probe": PROBE_NAME},
            },
            module_name="decision_log",
            event_type="create_decision",
        ),
        enrich_receipt(
            receipt={
                "project_id": "project-receipt-payload-probe",
                "artifact_path": "runtime://receipt-payload-probe/risk",
                "details": {"probe": PROBE_NAME},
            },
            module_name="risk_register",
            event_type="create_risk",
        ),
        enrich_receipt(
            receipt={
                "project_id": "project-receipt-payload-probe",
                "artifact_path": "runtime://receipt-payload-probe/assumption",
                "details": {"probe": PROBE_NAME},
            },
            module_name="assumption_log",
            event_type="create_assumption",
        ),
    ]

    results = [
        _check_receipt(f"sample_{index + 1}", receipt)
        for index, receipt in enumerate(sample_receipts)
    ]

    failed = [item for item in results if item.get("status") != "ok"]

    return {
        "probe": PROBE_NAME,
        "status": "passed" if not failed else "failed",
        "failed_count": len(failed),
        "failed": failed,
        "results": results,
        "mutation_allowed": False,
        "writes_performed": False,
    }


if __name__ == "__main__":
    output = run_probe()
    print(f"{PROBE_NAME}: {output['status'].upper()}")
    print("\nOUTPUT:\n", output)