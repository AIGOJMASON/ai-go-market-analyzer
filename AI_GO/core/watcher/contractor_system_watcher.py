from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.state_runtime.state_paths import contractor_project_root


SYSTEM_WATCHER_VERSION = "v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _resolve_project_root(project_id: str) -> Path:
    return contractor_project_root(project_id)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    return []


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean:
            continue
        try:
            payload = json.loads(clean)
        except Exception:
            continue
        if isinstance(payload, dict):
            records.append(payload)

    return records


def _latest_record(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}

    return records[-1]


def _load_workflow_state(project_root: Path) -> Dict[str, Any]:
    return _read_json(project_root / "workflow" / "workflow_state.json")


def _load_phase_instances(project_root: Path) -> List[Dict[str, Any]]:
    return _read_json_list(project_root / "workflow" / "phase_instances.json")


def _load_signoff_records(project_root: Path) -> List[Dict[str, Any]]:
    candidates = [
        project_root / "workflow" / "client_signoff_status.jsonl",
        project_root / "client_signoff_status.jsonl",
    ]

    for path in candidates:
        records = _read_jsonl(path)
        if records:
            return records

    return []


def _load_change_packets(project_root: Path) -> List[Dict[str, Any]]:
    candidates = [
        project_root / "change" / "change_packets.jsonl",
        project_root / "changes" / "change_packets.jsonl",
        project_root / "change_packets.jsonl",
    ]

    for path in candidates:
        records = _read_jsonl(path)
        if records:
            return records

    return []


def _load_delivery_records(project_root: Path) -> List[Dict[str, Any]]:
    delivery_root = project_root / "delivery"
    if not delivery_root.exists():
        return []

    records: List[Dict[str, Any]] = []
    for path in sorted(delivery_root.glob("*.json")):
        payload = _read_json(path)
        if payload:
            payload["_path"] = str(path)
            records.append(payload)

    return records


def _load_phase_closeout_artifacts(project_root: Path) -> List[Dict[str, Any]]:
    docs_root = project_root / "documents" / "phase_closeout_pdfs"
    if not docs_root.exists():
        return []

    records: List[Dict[str, Any]] = []
    for path in sorted(docs_root.glob("*.artifact.json")):
        payload = _read_json(path)
        if payload:
            payload["_path"] = str(path)
            records.append(payload)

    return records


def _find_phase(phase_instances: List[Dict[str, Any]], phase_id: str) -> Dict[str, Any]:
    for phase in phase_instances:
        if _safe_str(phase.get("phase_id")) == phase_id:
            return phase
    return {}


def _filter_by_phase(records: List[Dict[str, Any]], phase_id: str) -> List[Dict[str, Any]]:
    return [record for record in records if _safe_str(record.get("phase_id")) == phase_id]


def _change_is_blocking(packet: Dict[str, Any]) -> bool:
    status = _safe_str(packet.get("status") or packet.get("change_status")).lower()

    if status in {"approved", "rejected", "archived", "closed", "cancelled", "complete"}:
        return False

    if bool(packet.get("blocking") is True):
        return True

    impact = _safe_str(packet.get("impact") or packet.get("customer_impact")).lower()
    if impact in {"customer", "customer_impacting", "blocking"}:
        return True

    return status in {"draft", "requester_submitted", "pending_approvals", "open"}


def _check_project_exists(project_root: Path, errors: List[str], checks: Dict[str, Any]) -> None:
    exists = project_root.exists()
    checks["project_root_exists"] = exists
    if not exists:
        errors.append("project_root_missing")


def _check_workflow(
    *,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
    requested_phase_id: str,
    errors: List[str],
    warnings: List[str],
    checks: Dict[str, Any],
) -> None:
    current_phase_id = _safe_str(workflow_state.get("current_phase_id"))
    workflow_status = _safe_str(workflow_state.get("workflow_status"))

    checks["workflow_state_present"] = bool(workflow_state)
    checks["phase_instances_present"] = bool(phase_instances)
    checks["workflow_current_phase_id"] = current_phase_id
    checks["workflow_status"] = workflow_status

    if not workflow_state:
        errors.append("workflow_state_missing")

    if not phase_instances:
        errors.append("phase_instances_missing")

    effective_phase_id = requested_phase_id or current_phase_id
    matched_phase = _find_phase(phase_instances, effective_phase_id)

    checks["effective_phase_id"] = effective_phase_id
    checks["matched_phase_present"] = bool(matched_phase)

    if effective_phase_id and not matched_phase:
        errors.append("workflow_current_phase_not_found_in_phase_instances")

    if requested_phase_id and current_phase_id and requested_phase_id != current_phase_id:
        warnings.append("requested_phase_is_not_current_workflow_phase")


def _check_signoff_vs_workflow(
    *,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
    signoff_records: List[Dict[str, Any]],
    effective_phase_id: str,
    errors: List[str],
    warnings: List[str],
    checks: Dict[str, Any],
) -> Dict[str, Any]:
    phase_signoffs = _filter_by_phase(signoff_records, effective_phase_id)
    latest_signoff = _latest_record(phase_signoffs)

    phase = _find_phase(phase_instances, effective_phase_id)
    phase_status = _safe_str(phase.get("phase_status"))
    signoff_status = _safe_str(latest_signoff.get("status"))

    checks["signoff_record_count_for_phase"] = len(phase_signoffs)
    checks["latest_signoff_status"] = signoff_status
    checks["phase_status"] = phase_status

    if signoff_status == "sent" and phase_status not in {"awaiting_signoff", "complete", "closed"}:
        errors.append("signoff_sent_but_phase_not_in_signoff_posture")

    if signoff_status == "signed" and phase_status not in {"complete", "closed"}:
        warnings.append("signoff_signed_but_phase_not_complete_or_closed")

    if signoff_status == "declined" and phase_status in {"complete", "closed"}:
        errors.append("signoff_declined_but_phase_complete_or_closed")

    return latest_signoff


def _check_closeout_vs_signoff(
    *,
    latest_signoff: Dict[str, Any],
    closeout_artifacts: List[Dict[str, Any]],
    delivery_records: List[Dict[str, Any]],
    effective_phase_id: str,
    errors: List[str],
    warnings: List[str],
    checks: Dict[str, Any],
) -> None:
    signoff_status = _safe_str(latest_signoff.get("status"))
    artifact_id = _safe_str(
        latest_signoff.get("pdf_artifact_id")
        or latest_signoff.get("artifact_id")
        or latest_signoff.get("pdf_artifact")
    )

    phase_artifacts = _filter_by_phase(closeout_artifacts, effective_phase_id)
    phase_delivery = _filter_by_phase(delivery_records, effective_phase_id)

    checks["phase_closeout_artifact_count"] = len(phase_artifacts)
    checks["phase_delivery_record_count"] = len(phase_delivery)
    checks["latest_signoff_artifact_id"] = artifact_id

    if signoff_status in {"sent", "signed"} and not phase_artifacts:
        errors.append("signoff_exists_but_phase_closeout_artifact_missing")

    if signoff_status in {"sent", "signed"} and not phase_delivery:
        errors.append("signoff_exists_but_delivery_record_missing")

    if artifact_id:
        artifact_found = any(
            _safe_str(item.get("artifact_id")) == artifact_id for item in phase_artifacts
        )
        checks["latest_signoff_artifact_found"] = artifact_found
        if not artifact_found:
            warnings.append("signoff_artifact_id_not_found_in_closeout_artifacts")


def _check_changes_vs_closeout(
    *,
    change_packets: List[Dict[str, Any]],
    effective_phase_id: str,
    errors: List[str],
    warnings: List[str],
    checks: Dict[str, Any],
) -> None:
    phase_changes = _filter_by_phase(change_packets, effective_phase_id)
    blocking = [packet for packet in phase_changes if _change_is_blocking(packet)]

    checks["phase_change_packet_count"] = len(phase_changes)
    checks["blocking_change_packet_count"] = len(blocking)

    if blocking:
        errors.append("blocking_unresolved_change_exists_for_phase")


def _check_report_vs_project(
    *,
    report: Optional[Dict[str, Any]],
    project_id: str,
    errors: List[str],
    warnings: List[str],
    checks: Dict[str, Any],
) -> None:
    report_payload = _safe_dict(report)

    if not report_payload:
        checks["report_supplied"] = False
        return

    checks["report_supplied"] = True

    subject_id = _safe_str(report_payload.get("subject_id"))
    report_project_id = _safe_str(report_payload.get("project_id"))

    checks["report_subject_id"] = subject_id
    checks["report_project_id"] = report_project_id

    if subject_id and subject_id != project_id:
        errors.append("report_subject_id_does_not_match_project_id")

    if report_project_id and report_project_id != project_id:
        errors.append("report_project_id_does_not_match_project_id")


def watch_contractor_system(
    *,
    project_id: str,
    phase_id: str = "",
    report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)

    errors: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, Any] = {}

    if not clean_project_id:
        errors.append("project_id_required")

    project_root = _resolve_project_root(clean_project_id) if clean_project_id else Path("")
    checks["project_root"] = str(project_root)

    if clean_project_id:
        _check_project_exists(project_root, errors, checks)

    workflow_state = _load_workflow_state(project_root)
    phase_instances = _load_phase_instances(project_root)
    signoff_records = _load_signoff_records(project_root)
    change_packets = _load_change_packets(project_root)
    delivery_records = _load_delivery_records(project_root)
    closeout_artifacts = _load_phase_closeout_artifacts(project_root)

    _check_workflow(
        workflow_state=workflow_state,
        phase_instances=phase_instances,
        requested_phase_id=clean_phase_id,
        errors=errors,
        warnings=warnings,
        checks=checks,
    )

    effective_phase_id = _safe_str(checks.get("effective_phase_id"))

    latest_signoff = {}
    if effective_phase_id:
        latest_signoff = _check_signoff_vs_workflow(
            workflow_state=workflow_state,
            phase_instances=phase_instances,
            signoff_records=signoff_records,
            effective_phase_id=effective_phase_id,
            errors=errors,
            warnings=warnings,
            checks=checks,
        )

        _check_closeout_vs_signoff(
            latest_signoff=latest_signoff,
            closeout_artifacts=closeout_artifacts,
            delivery_records=delivery_records,
            effective_phase_id=effective_phase_id,
            errors=errors,
            warnings=warnings,
            checks=checks,
        )

        _check_changes_vs_closeout(
            change_packets=change_packets,
            effective_phase_id=effective_phase_id,
            errors=errors,
            warnings=warnings,
            checks=checks,
        )

    _check_report_vs_project(
        report=report,
        project_id=clean_project_id,
        errors=errors,
        warnings=warnings,
        checks=checks,
    )

    valid = len(errors) == 0

    return {
        "artifact_type": "contractor_system_watcher_validation",
        "artifact_version": SYSTEM_WATCHER_VERSION,
        "generated_at": _utc_now_iso(),
        "profile": "contractor_system",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": clean_project_id,
        "phase_id": effective_phase_id,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "branches_checked": [
            "workflow",
            "signoff",
            "phase_closeout",
            "delivery",
            "change",
            "report",
        ],
        "policy": {
            "read_only": True,
            "mutation_allowed": False,
            "execution_allowed": False,
            "system_watcher_only": True,
        },
        "sealed": True,
    }