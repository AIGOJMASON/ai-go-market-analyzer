from __future__ import annotations

try:
    from AI_GO.api.outcome_ingress_schema import ALLOWED_OUTCOME_INGRESS_SOURCES
except ImportError:
    from api.outcome_ingress_schema import ALLOWED_OUTCOME_INGRESS_SOURCES


def validate_outcome_ingress_request(request_payload: dict) -> None:
    closeout_id = str(request_payload.get("closeout_id", "")).strip()
    if not closeout_id:
        raise ValueError("missing_closeout_id")

    actual_outcome = request_payload.get("actual_outcome")
    if actual_outcome is None or not str(actual_outcome).strip():
        raise ValueError("missing_actual_outcome")

    source = str(request_payload.get("source", "manual")).strip().lower()
    if source not in ALLOWED_OUTCOME_INGRESS_SOURCES:
        raise ValueError("invalid_outcome_ingress_source")


def validate_closeout_artifact_linkage(
    *,
    closeout_artifact: dict,
    request_payload: dict,
) -> None:
    artifact_closeout_id = str(closeout_artifact.get("closeout_id", "")).strip()
    request_closeout_id = str(request_payload.get("closeout_id", "")).strip()

    if not artifact_closeout_id:
        raise ValueError("missing_closeout_id_in_closeout_artifact")

    if artifact_closeout_id != request_closeout_id:
        raise ValueError("closeout_id_mismatch")


def build_observed_outcome_view(request_payload: dict) -> dict:
    return {
        "actual_outcome": str(request_payload.get("actual_outcome", "")).strip(),
        "source": str(request_payload.get("source", "manual")).strip().lower(),
        "notes": str(request_payload.get("notes", "")).strip(),
        "observed_at": request_payload.get("observed_at"),
    }