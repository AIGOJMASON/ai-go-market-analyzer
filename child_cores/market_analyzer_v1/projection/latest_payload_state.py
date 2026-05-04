from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


def _resolve_project_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / "app.py").exists() and (candidate / "state").exists():
            return candidate
    for candidate in current.parents:
        if (candidate / "app.py").exists():
            return candidate
    return current.parents[3]


PROJECT_ROOT = _resolve_project_root()
LATEST_OPERATOR_PAYLOAD_PATH = (
    PROJECT_ROOT / "state" / "operator_dashboard" / "latest_operator_payload.json"
)


def _persist_latest_payload(path: Path, payload: Dict[str, Any]) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="market_operator_payload_persistence",
        persistence_type="market_operator_latest_payload",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_latest_operator_payload",
            "child_core_id": "market_analyzer_v1",
            "layer": "projection.latest_payload_state",
        },
    )


def read_latest_operator_payload() -> dict[str, Any]:
    if not LATEST_OPERATOR_PAYLOAD_PATH.exists():
        return {
            "state": "absent",
            "reason": "no_latest_operator_payload_recorded",
            "path": str(LATEST_OPERATOR_PAYLOAD_PATH),
        }

    try:
        parsed = json.loads(LATEST_OPERATOR_PAYLOAD_PATH.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            return parsed
        return {
            "state": "error",
            "reason": "latest_operator_payload_not_dict",
            "path": str(LATEST_OPERATOR_PAYLOAD_PATH),
        }
    except Exception as exc:
        return {
            "state": "error",
            "reason": "latest_operator_payload_unreadable",
            "path": str(LATEST_OPERATOR_PAYLOAD_PATH),
            "error": str(exc),
        }


def persist_latest_operator_payload(result: dict[str, Any]) -> None:
    if not isinstance(result, dict):
        return

    try:
        payload = dict(result)
        payload.setdefault("artifact_type", "market_analyzer_latest_operator_payload")
        payload.setdefault("artifact_version", "northstar_market_projection_v1")
        payload["classification"] = {
            "persistence_type": "market_operator_latest_payload",
            "mutation_class": "market_operator_payload_persistence",
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "authority_mutation_allowed": False,
            "advisory_only": True,
        }
        payload["authority"] = {
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_recommendation": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
        }
        payload["sealed"] = True

        _persist_latest_payload(LATEST_OPERATOR_PAYLOAD_PATH, payload)
    except Exception:
        traceback.print_exc()