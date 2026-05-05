from __future__ import annotations

import json
from pathlib import Path

from AI_GO.core.watcher.contractor_system_watcher import watch_contractor_system


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload))
        handle.write("\n")


def run_probe() -> dict:
    project_id = "project-system-watcher-probe"
    phase_id = "phase-system-watcher-probe"

    root = Path("AI_GO/state/contractor_builder_v1/projects/by_project") / project_id

    _write_json(
        root / "workflow" / "workflow_state.json",
        {
            "project_id": project_id,
            "workflow_status": "active",
            "current_phase_id": phase_id,
        },
    )

    _write_json(
        root / "workflow" / "phase_instances.json",
        [
            {
                "project_id": project_id,
                "phase_id": phase_id,
                "phase_name": "System Watcher Probe Phase",
                "phase_status": "awaiting_signoff",
            }
        ],
    )

    _append_jsonl(
        root / "workflow" / "client_signoff_status.jsonl",
        {
            "project_id": project_id,
            "phase_id": phase_id,
            "status": "sent",
            "artifact_id": "artifact-system-watcher-probe",
        },
    )

    _write_json(
        root
        / "documents"
        / "phase_closeout_pdfs"
        / "artifact-system-watcher-probe.artifact.json",
        {
            "artifact_id": "artifact-system-watcher-probe",
            "project_id": project_id,
            "phase_id": phase_id,
            "pdf_path": "state/demo/system_watcher_probe.txt",
        },
    )

    _write_json(
        root / "delivery" / "email-system-watcher-probe.json",
        {
            "delivery_id": "email-system-watcher-probe",
            "project_id": project_id,
            "phase_id": phase_id,
            "delivery_status": "sent",
        },
    )

    result = watch_contractor_system(
        project_id=project_id,
        phase_id=phase_id,
        report={
            "subject_id": project_id,
            "report_id": "report-system-watcher-probe",
            "status": "generated",
        },
    )

    assert result["valid"] is True
    assert result["status"] == "passed"
    assert result["checks"]["project_root_exists"] is True
    assert result["checks"]["matched_phase_present"] is True
    assert result["checks"]["phase_closeout_artifact_count"] >= 1
    assert result["checks"]["phase_delivery_record_count"] >= 1

    broken = watch_contractor_system(
        project_id=project_id,
        phase_id=phase_id,
        report={
            "subject_id": "wrong-project-id",
            "report_id": "report-system-watcher-probe",
        },
    )

    assert broken["valid"] is False
    assert "report_subject_id_does_not_match_project_id" in broken["errors"]

    return {
        "status": "passed",
        "valid_result": result,
        "broken_result": broken,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_SYSTEM_WATCHER_PROBE: PASS")
    print(json.dumps(output, indent=2))