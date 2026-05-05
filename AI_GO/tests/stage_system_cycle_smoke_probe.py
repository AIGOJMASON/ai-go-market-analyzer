from __future__ import annotations

import json
from pathlib import Path

from system_cycle import SystemCycle


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    cycle = SystemCycle(
        project_root=project_root,
        once=True,
        iterations=1,
        quiet=True,
    )
    exit_code = cycle.run()
    _assert(exit_code in (0, 1), "system cycle returned invalid exit code")

    status_path = project_root / "state" / "system_cycle" / "current" / "system_cycle_status.json"
    _assert(status_path.exists(), "current system cycle status file was not created")

    status_payload = json.loads(status_path.read_text(encoding="utf-8"))
    _assert("latest_cycle_id" in status_payload, "missing latest_cycle_id")
    _assert("latest_receipt_path" in status_payload, "missing latest_receipt_path")
    _assert("step_statuses" in status_payload, "missing step_statuses")

    receipt_path = Path(status_payload["latest_receipt_path"])
    _assert(receipt_path.exists(), "receipt path in status file does not exist")

    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    _assert("steps" in receipt_payload, "receipt missing steps")
    _assert(isinstance(receipt_payload["steps"], list), "receipt steps is not a list")

    step_names = {step["step_name"] for step in receipt_payload["steps"]}
    expected = {
        "live_trigger",
        "continuity_weighting",
        "continuity_weighting_refinement_bridge",
        "refinement_to_pm_bridge",
        "visibility",
    }
    missing = expected - step_names
    _assert(not missing, f"missing expected step names: {sorted(missing)}")

    print(
        {
            "passed": 5,
            "failed": 0,
            "results": [
                {"case": "case_01_status_written", "status": "passed"},
                {"case": "case_02_receipt_written", "status": "passed"},
                {"case": "case_03_steps_present", "status": "passed"},
                {"case": "case_04_cycle_id_present", "status": "passed"},
                {"case": "case_05_smoke_completed", "status": "passed"},
            ],
        }
    )


if __name__ == "__main__":
    main()