from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENGINE_DIR = os.path.join(BASE_DIR, "engines", "refinement_arbitrator")
RUNTIME_DIR = os.path.join(BASE_DIR, "core", "runtime")
PM_REFINEMENT_DIR = os.path.join(BASE_DIR, "PM_CORE", "refinement")
PM_SMI_DIR = os.path.join(BASE_DIR, "PM_CORE", "smi")
PM_STRATEGY_DIR = os.path.join(BASE_DIR, "PM_CORE", "strategy")

for path in [ENGINE_DIR, RUNTIME_DIR, PM_REFINEMENT_DIR, PM_SMI_DIR, PM_STRATEGY_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from engine import run_arbitration  # noqa: E402
from policies import EntropyState  # noqa: E402
from router import route_payload  # noqa: E402
from arbitration_intake import intake_arbitration_decision  # noqa: E402
from pm_continuity import update_pm_continuity  # noqa: E402
from pm_strategy import run_pm_strategy  # noqa: E402


def make_packet() -> dict:
    return {
        "packet_id": "WR-RESEARCH-PACKET-2026-0022",
        "source_core": "research_core",
        "packet_type": "planning_brief",
        "title": "Stage 18 closeout PM strategy signal",
        "summary": (
            "Research indicates recurring local contractor proposal workflow demand that should progress through "
            "arbitration, PM intake, PM continuity, and finally PM strategy to produce a governed decision packet."
        ),
        "source_refs": ["SRC-A", "SRC-B"],
        "trust_class": "screened",
        "confidence": 0.89,
        "scope": "core",
        "tags": ["pm_core", "proposal", "contractor", "continuity", "strategy", "louisville"],
        "screening_status": "screened",
        "issuing_authority": "RESEARCH_CORE",
        "timestamp": "2026-03-17T22:00:00Z",
        "target_core_hint": "contractor_proposals_core",
        "domain_hint": "proposals",
        "notes": "Stage 18 closeout probe packet.",
    }


def main() -> int:
    packet = make_packet()

    route_one = route_payload(packet)
    assert route_one["status"] == "routable"
    assert route_one["target_surface"] == "engines.refinement_arbitrator"

    arbitration = run_arbitration(
        packet,
        entropy_state=EntropyState(entropy_status="medium", gravity_status="high", grace_status="medium"),
        persist=True,
    )
    assert arbitration["issuing_layer"] == "REFINEMENT_ARBITRATOR"

    route_two = route_payload(arbitration)
    assert route_two["status"] == "routable"
    assert route_two["target_surface"] == "pm.refinement.arbitration_intake"

    pm_intake = intake_arbitration_decision(arbitration, persist=True)
    assert pm_intake["record"]["status"] == "accepted_for_pm_review"

    route_three = route_payload(pm_intake["record"])
    assert route_three["status"] == "routable"
    assert route_three["target_surface"] == "pm.smi.continuity"

    continuity = update_pm_continuity(pm_intake["record"], persist=True)
    assert continuity["update"]["update_type"] == "pm_continuity_update"

    route_four = route_payload(continuity["update"])
    assert route_four["status"] == "routable"
    assert route_four["target_surface"] == "pm.strategy"

    strategy = run_pm_strategy(continuity["update"], persist=True)
    assert strategy["decision_packet"]["packet_type"] == "pm_decision_packet"
    assert strategy["receipt"]["receipt_type"] == "pm_strategy_receipt"
    assert os.path.exists(strategy["paths"]["state_path"])
    assert os.path.exists(strategy["paths"]["ledger_path"])

    state = strategy["state"]
    assert state["total_decisions"] >= 1
    assert strategy["decision_packet"]["packet_id"] in state["recent_decision_ids"]

    disallowed_keys = {
        "child_core_activated",
        "routing_complete",
        "pm_routing_execution",
        "canon_mutation_complete",
    }
    assert not (disallowed_keys & set(strategy["decision_packet"].keys()))
    assert not (disallowed_keys & set(strategy.keys()))

    print("STAGE 18 CLOSEOUT PROBE: PASS")
    print(json.dumps(
        {
            "route_one": route_one,
            "arbitration": arbitration,
            "route_two": route_two,
            "pm_intake": pm_intake,
            "route_three": route_three,
            "continuity": continuity,
            "route_four": route_four,
            "strategy": strategy,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())