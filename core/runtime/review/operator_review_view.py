from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict


FORBIDDEN_FIELDS = {
    "internal_state",
    "internal_notes",
    "private_notes",
    "debug",
    "debug_trace",
    "traceback",
    "_internal",
    "_debug",
    "_private",
}


class OperatorReviewError(ValueError):
    pass


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise OperatorReviewError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorReviewError(f"{name} must be a dict")
    return value


def _require_field(payload: Dict[str, Any], field_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise OperatorReviewError(f"payload.{field_name} is required")
    return value


def build_operator_review_view(
    case_closeout_record: Dict[str, Any],
    issuing_authority: str = "RUNTIME_OPERATOR_REVIEW",
) -> Dict[str, Any]:
    _assert_no_internal_field_leakage(case_closeout_record)

    case_closeout_record = _require_dict(
        "case_closeout_record",
        deepcopy(case_closeout_record),
    )

    if case_closeout_record.get("artifact_type") != "case_closeout_record":
        raise OperatorReviewError("artifact_type must be 'case_closeout_record'")

    payload = case_closeout_record.get("payload")
    if not isinstance(payload, dict):
        raise OperatorReviewError("payload must be a dict")

    if payload.get("sealed") is not True:
        raise OperatorReviewError("case_closeout_record.payload.sealed must be True")

    case_id = _require_field(payload, "case_id")
    closeout_state = _require_field(payload, "closeout_state")
    final_state = _require_field(payload, "final_state")
    target_child_core = _require_field(payload, "target_child_core")
    intake_decision = _require_field(payload, "intake_decision")

    created_at = payload.get("created_at")
    review_generated_at = _utc_timestamp()

    return {
        "artifact_type": "operator_review_view",
        "payload": {
            "case_id": case_id,
            "closeout_state": closeout_state,
            "final_state": final_state,
            "target_child_core": target_child_core,
            "intake_decision": intake_decision,
            "created_at": created_at,
            "review_generated_at": review_generated_at,
            "issuing_authority": issuing_authority,
            "sealed": True,
        },
    }