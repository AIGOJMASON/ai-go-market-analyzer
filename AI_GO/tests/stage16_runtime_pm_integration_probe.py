from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENGINE_DIR = os.path.join(BASE_DIR, "engines", "refinement_arbitrator")
RUNTIME_DIR = os.path.join(BASE_DIR, "core", "runtime")
PM_REFINEMENT_DIR = os.path.join(BASE_DIR, "PM_CORE", "refinement")

for path in [ENGINE_DIR, RUNTIME_DIR, PM_REFINEMENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from engine import run_arbitration  # noqa: E402
from policies import EntropyState  # noqa: E402
from router import route_payload  # noqa: E402
from arbitration_intake import intake_arbitration_decision  # noqa: E402


def make_packet() -> dict:
    return {
        "packet_id": "WR-RESEARCH-PACKET-2026-0017",
        "source_core": "research_core",
        "packet_type": "planning_brief",
        "title": "Louisville contractor proposal workflow demand signal",
        "summary": (
            "Research indicates repeated local demand for contractor estimate logic, proposal workflow "
            "improvements, and change order support in Louisville small-business operations."
        ),
        "source_refs": ["SRC-A", "SRC-B"],
        "trust_class": "screened",
        "confidence": 0.86,
        "scope": "core",
        "tags": ["pm_core", "research_ingress", "proposal", "contractor", "louisville"],
        "screening_status": "screened",
        "issuing_authority": "RESEARCH_CORE",
        "timestamp": "2026-03-17T18:00:00Z",
        "target_core_hint": "contractor_proposals_core",
        "domain_hint": "proposals",
        "notes": "Structured local signal suitable for downstream PM planning review.",
    }


def main() -> int:
    packet = make_packet()

    route_one = route_payload(packet)
    assert route_one["status"] == "routable"
    assert route_one["target_surface"] == "engines.refinement_arbitrator"

    arbitration = run_arbitration(
        packet,
        entropy_state=EntropyState(entropy_status="medium", gravity_status="high", grace_status="medium"),
    )
    assert arbitration["issuing_layer"] == "REFINEMENT_ARBITRATOR"

    route_two = route_payload(arbitration)
    assert route_two["status"] == "routable"
    assert route_two["target_surface"] == "pm.refinement.arbitration_intake"

    pm_intake = intake_arbitration_decision(arbitration)
    assert pm_intake["record"]["status"] == "accepted_for_pm_review"
    assert pm_intake["record"]["source_arbitration_id"] == arbitration["arbitration_id"]
    assert pm_intake["record"]["recommended_action"] == arbitration["recommended_action"]
    assert "routing_complete" not in pm_intake["record"]
    assert "child_core_activated" not in pm_intake["record"]
    assert "pm_continuity_written" not in pm_intake["record"]

    print("STAGE 16 RUNTIME + PM INTEGRATION PROBE: PASS")
    print(json.dumps(
        {
            "route_one": route_one,
            "arbitration": arbitration,
            "route_two": route_two,
            "pm_intake": pm_intake,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())