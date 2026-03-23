from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENGINE_DIR = os.path.join(BASE_DIR, "engines", "refinement_arbitrator")
RUNTIME_DIR = os.path.join(BASE_DIR, "core", "runtime")
PM_REFINEMENT_DIR = os.path.join(BASE_DIR, "PM_CORE", "refinement")
PM_SMI_DIR = os.path.join(BASE_DIR, "PM_CORE", "smi")

for path in [ENGINE_DIR, RUNTIME_DIR, PM_REFINEMENT_DIR, PM_SMI_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from engine import run_arbitration  # noqa: E402
from policies import EntropyState  # noqa: E402
from arbitration_intake import intake_arbitration_decision  # noqa: E402
from pm_continuity import update_pm_continuity  # noqa: E402


def make_packet() -> dict:
    return {
        "packet_id": "WR-RESEARCH-PACKET-2026-0020",
        "source_core": "research_core",
        "packet_type": "planning_brief",
        "title": "Stage 17 PM continuity probe signal",
        "summary": (
            "Research indicates recurring local contractor proposal workflow demand that should be visible "
            "to PM continuity after lawful arbitration and PM intake."
        ),
        "source_refs": ["SRC-A", "SRC-B"],
        "trust_class": "screened",
        "confidence": 0.84,
        "scope": "core",
        "tags": ["pm_core", "proposal", "contractor", "continuity", "louisville"],
        "screening_status": "screened",
        "issuing_authority": "RESEARCH_CORE",
        "timestamp": "2026-03-17T20:00:00Z",
        "target_core_hint": "contractor_proposals_core",
        "domain_hint": "proposals",
        "notes": "Stage 17 PM continuity probe packet.",
    }


def main() -> int:
    packet = make_packet()
    arbitration = run_arbitration(
        packet,
        entropy_state=EntropyState(entropy_status="medium", gravity_status="high", grace_status="medium"),
        persist=True,
    )
    pm_intake = intake_arbitration_decision(arbitration, persist=True)
    continuity = update_pm_continuity(pm_intake["record"], persist=True)

    assert continuity["update"]["update_type"] == "pm_continuity_update"
    assert continuity["receipt"]["receipt_type"] == "pm_continuity_receipt"
    assert os.path.exists(continuity["paths"]["state_path"])
    assert os.path.exists(continuity["paths"]["ledger_path"])
    assert os.path.exists(continuity["paths"]["unresolved_path"])

    state_snapshot = continuity["update"]["state_snapshot"]
    assert state_snapshot["total_pm_intake_records"] >= 1
    assert pm_intake["record"]["pm_intake_id"] in state_snapshot["recent_pm_intake_ids"]
    assert pm_intake["record"]["source_arbitration_id"] in state_snapshot["recent_source_arbitration_ids"]

    disallowed_keys = {
        "routing_complete",
        "child_core_activated",
        "pm_routing_execution",
        "canon_mutation_complete",
    }
    assert not (disallowed_keys & set(continuity["update"].keys()))

    print("STAGE 17 PM CONTINUITY PROBE: PASS")
    print(json.dumps(
        {
            "arbitration": arbitration,
            "pm_intake": pm_intake,
            "continuity": continuity,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())