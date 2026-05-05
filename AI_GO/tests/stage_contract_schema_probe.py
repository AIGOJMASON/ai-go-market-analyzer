from __future__ import annotations

import importlib
from typing import Any, Dict, List


PROBE_NAME = "STAGE_CONTRACT_SCHEMA_PROBE"


def _missing_fields(payload: Dict[str, Any], required: List[str]) -> List[str]:
    return [field for field in required if field not in payload or payload.get(field) in ("", None)]


def _run_validator(module: Any, validator_name: str, payload: Dict[str, Any]) -> List[str]:
    validator = getattr(module, validator_name, None)
    if validator is None:
        return [f"missing_validator:{validator_name}"]

    result = validator(payload)
    if result is None:
        return []
    if isinstance(result, list):
        return [str(item) for item in result]
    if result is True:
        return []
    if result is False:
        return [f"validator_failed:{validator_name}"]

    return [f"unexpected_validator_result:{validator_name}:{type(result).__name__}"]


def _check_contract(
    *,
    label: str,
    module_path: str,
    builder_name: str,
    validator_name: str,
    kwargs: Dict[str, Any],
    required_fields: List[str],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(module_path)
        builder = getattr(module, builder_name, None)

        if builder is None:
            return {
                "label": label,
                "status": "failed",
                "module": module_path,
                "error": f"missing_builder:{builder_name}",
            }

        artifact = builder(**kwargs)

        if not isinstance(artifact, dict):
            return {
                "label": label,
                "status": "failed",
                "module": module_path,
                "error": f"builder_returned_non_dict:{type(artifact).__name__}",
            }

        missing = _missing_fields(artifact, required_fields)
        validation_errors = _run_validator(module, validator_name, artifact)

        if missing or validation_errors:
            return {
                "label": label,
                "status": "failed",
                "module": module_path,
                "missing_fields": missing,
                "validation_errors": validation_errors,
                "artifact_keys": sorted(artifact.keys()),
            }

        return {
            "label": label,
            "status": "ok",
            "module": module_path,
            "artifact_keys": sorted(artifact.keys()),
        }

    except Exception as exc:
        return {
            "label": label,
            "status": "failed",
            "module": module_path,
            "error": f"{type(exc).__name__}: {exc}",
        }


def run_probe() -> Dict[str, Any]:
    contracts = [
        {
            "label": "decision_log",
            "module_path": "AI_GO.child_cores.contractor_builder_v1.decision_log.decision_schema",
            "builder_name": "build_decision_entry",
            "validator_name": "validate_decision_entry",
            "kwargs": {
                "decision_id": "decision-contract-schema-probe",
                "project_id": "project-contract-schema-probe",
                "title": "Contract schema probe decision",
                "decision_type": "Scope_Clarification",
                "phase_id": "phase-contract-schema-probe",
                "notes_internal": "Read-only schema probe.",
            },
            "required_fields": [
                "schema_version",
                "decision_id",
                "project_id",
                "title",
                "decision_type",
                "decision_status",
                "context_lock",
                "declared_impact",
                "integrity",
            ],
        },
        {
            "label": "risk_register",
            "module_path": "AI_GO.child_cores.contractor_builder_v1.risk_register.risk_schema",
            "builder_name": "build_risk_entry",
            "validator_name": "validate_risk_entry",
            "kwargs": {
                "risk_id": "risk-contract-schema-probe",
                "project_id": "project-contract-schema-probe",
                "category": "Other",
                "description": "Contract schema probe risk.",
                "probability": "Moderate",
                "impact_level": "Moderate",
                "mitigation_strategy": "Observe and document.",
                "mitigation_owner": "system",
                "notes": "Read-only schema probe.",
            },
            "required_fields": [
                "schema_version",
                "risk_id",
                "project_id",
                "category",
                "description",
                "probability",
                "impact_level",
                "mitigation_strategy",
                "mitigation_owner",
                "status",
                "integrity",
            ],
        },
        {
            "label": "assumption_log",
            "module_path": "AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_schema",
            "builder_name": "build_assumption_entry",
            "validator_name": "validate_assumption_entry",
            "kwargs": {
                "assumption_id": "assumption-contract-schema-probe",
                "project_id": "project-contract-schema-probe",
                "statement": "Contract schema probe assumption.",
                "source_type": "Other",
                "source_reference": "stage_contract_schema_probe",
                "logged_by": "system",
                "impact_if_false": "Schema contract would need repair.",
                "notes": "Read-only schema probe.",
            },
            "required_fields": [
                "schema_version",
                "assumption_id",
                "project_id",
                "statement",
                "source_type",
                "source_reference",
                "date_logged",
                "logged_by",
                "validation_status",
                "integrity",
            ],
        },
    ]

    results = [_check_contract(**contract) for contract in contracts]
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