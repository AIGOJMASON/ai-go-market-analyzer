from __future__ import annotations

import inspect
import os
from pathlib import Path
from typing import Any, Dict, Mapping

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "awareness_persistence"
RECEIPT_MUTATION_CLASS = "receipt"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_activate_child_core": False,
    "can_mutate_child_core_lifecycle": False,
    "can_mutate_pm_routing": False,
    "can_mutate_research_truth": False,
    "can_mutate_continuity_truth": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "refinement_arbitrator_layer_decision_only",
}


def _repo_root() -> str:
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def refinement_state_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "state", "refinement_arbitrator", "current"))


def refinement_receipts_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "state", "refinement_arbitrator", "receipts"))


def pm_receipts_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "PM_CORE", "state", "receipts"))


def _normalize_payload(
    payload: Mapping[str, Any],
    *,
    persistence_type: str,
    mutation_class: str,
    advisory_only: bool,
) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = mutation_class
    normalized["advisory_only"] = advisory_only
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["pm_routing_mutation_allowed"] = False
    normalized["research_truth_mutation_allowed"] = False
    normalized["child_core_lifecycle_mutation_allowed"] = False
    normalized["sealed"] = True
    return normalized


def persist_json(
    path: str,
    payload: Mapping[str, Any],
    *,
    persistence_type: str = "refinement_arbitrator_artifact",
    mutation_class: str = MUTATION_CLASS,
    advisory_only: bool = True,
) -> str:
    target = Path(path)
    normalized = _normalize_payload(
        payload,
        persistence_type=persistence_type,
        mutation_class=mutation_class,
        advisory_only=advisory_only,
    )

    kwargs = {
        "path": target,
        "output_path": target,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": advisory_only,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(target, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or target)

    return str(target)


def persist_arbitration_decision(decision: Mapping[str, Any]) -> str:
    arbitration_id = str(decision["arbitration_id"])
    filename = f"{arbitration_id}__decision.json"
    path = os.path.join(refinement_state_dir(), filename)
    return persist_json(
        path,
        decision,
        persistence_type="refinement_arbitrator_decision",
        mutation_class=MUTATION_CLASS,
        advisory_only=True,
    )


def persist_arbitration_receipt(receipt: Mapping[str, Any]) -> str:
    arbitration_id = str(receipt["arbitration_id"])
    filename = f"{arbitration_id}__receipt.json"
    path = os.path.join(refinement_receipts_dir(), filename)
    return persist_json(
        path,
        receipt,
        persistence_type="refinement_arbitrator_receipt",
        mutation_class=RECEIPT_MUTATION_CLASS,
        advisory_only=False,
    )


def persist_pm_intake_receipt(receipt: Mapping[str, Any]) -> str:
    pm_intake_id = str(receipt["pm_intake_id"])
    filename = f"{pm_intake_id}__pm_intake_receipt.json"
    path = os.path.join(pm_receipts_dir(), filename)
    return persist_json(
        path,
        receipt,
        persistence_type="pm_refinement_intake_receipt",
        mutation_class=RECEIPT_MUTATION_CLASS,
        advisory_only=False,
    )