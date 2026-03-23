from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENGINE_DIR = os.path.join(BASE_DIR, "engines", "refinement_arbitrator")
RUNTIME_DIR = os.path.join(BASE_DIR, "core", "runtime")
PM_REFINEMENT_DIR = os.path.join(BASE_DIR, "PM_CORE", "refinement")
ENGINES_DIR = os.path.join(BASE_DIR, "engines")

for path in [ENGINE_DIR, RUNTIME_DIR, PM_REFINEMENT_DIR, ENGINES_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from engine import run_arbitration  # noqa: E402
from policies import EntropyState  # noqa: E402
from router import route_payload  # noqa: E402
from arbitration_intake import intake_arbitration_decision  # noqa: E402
from loader import load_refinement_arbitrator  # noqa: E402
from engine_registry import get_engine_surface  # noqa: E402


def make_packet() -> dict:
    return {
        "packet_id": "WR-RESEARCH-PACKET-2026-0019",
        "source_core": "research_core",
        "packet_type": "planning_brief",
        "title": "Louisville contractor proposal workflow demand signal closeout probe",
        "summary": (
            "Research indicates repeated local demand for contractor estimate logic, proposal workflow "
            "improvements, and change order support in Louisville small-business operations. "
            "Signal appears structurally useful for PM review and proposal-core conditioning."
        ),
        "source_refs": ["SRC-A", "SRC-B"],
        "trust_class": "screened",
        "confidence": 0.88,
        "scope": "core",
        "tags": ["pm_core", "research_ingress", "proposal", "contractor", "louisville"],
        "screening_status": "screened",
        "issuing_authority": "RESEARCH_CORE",
        "timestamp": "2026-03-17T19:00:00Z",
        "target_core_hint": "contractor_proposals_core",
        "domain_hint": "proposals",
        "notes": "Closeout probe packet for Stage 16 final validation.",
    }


def main() -> int:
    packet = make_packet()

    route_one = route_payload(packet)
    assert route_one["status"] == "routable"
    assert route_one["target_surface"] == "engines.refinement_arbitrator"

    loaded = load_refinement_arbitrator()
    arbitration = loaded(
        packet,
        entropy_state=EntropyState(entropy_status="medium", gravity_status="high", grace_status="medium"),
        persist=True,
    )
    assert arbitration["issuing_layer"] == "REFINEMENT_ARBITRATOR"
    assert os.path.exists(arbitration["decision_path"])
    assert os.path.exists(arbitration["receipt_path"])

    route_two = route_payload(arbitration)
    assert route_two["status"] == "routable"
    assert route_two["target_surface"] == "pm.refinement.arbitration_intake"

    pm_intake = intake_arbitration_decision(arbitration, persist=True)
    assert pm_intake["record"]["status"] == "accepted_for_pm_review"
    assert os.path.exists(pm_intake["receipt"]["receipt_path"])

    engine_surface = get_engine_surface("refinement_arbitrator")
    assert engine_surface.engine_id == "refinement_arbitrator"

    disallowed_keys = {
        "routing_complete",
        "child_core_activated",
        "pm_continuity_written",
    }
    assert not (disallowed_keys & set(arbitration.keys()))
    assert not (disallowed_keys & set(pm_intake["record"].keys()))

    print("STAGE 16 CLOSEOUT PROBE: PASS")
    print(json.dumps(
        {
            "route_one": route_one,
            "arbitration": arbitration,
            "route_two": route_two,
            "pm_intake": pm_intake,
            "engine_surface": {
                "engine_id": engine_surface.engine_id,
                "authority_class": engine_surface.authority_class,
                "entrypoint": engine_surface.entrypoint,
            },
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())