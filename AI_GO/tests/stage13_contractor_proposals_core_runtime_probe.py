from __future__ import annotations

from core.runtime.router import run_research_command


def run() -> dict:
    """
    Stage 13 probe:
    sends a contractor proposal-oriented research payload through runtime,
    PM refinement, child-core alignment, active child-core handoff,
    contractor_proposals_core execution, watcher verification, and child-core SMI.
    """
    payload = {
        "packet_id": "stage13_contractor_probe_0001",
        "title": "Louisville contractor proposal workflow demand",
        "summary": "Research indicates demand for contractor proposal, estimate, and quoting workflow support for local service businesses.",
        "tags": ["contractor", "proposal", "estimate", "workflow"],
    }
    return run_research_command(payload)


if __name__ == "__main__":
    print(run())