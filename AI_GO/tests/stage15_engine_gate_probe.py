from __future__ import annotations

from core.runtime.router import run_research_command


def run() -> dict:
    """
    Stage 15 probe set:
    - reasoning refinement through Curved Mirror
    - narrative refinement through Rosetta
    - dual refinement through both engines
    """
    results = []

    results.append(
        run_research_command(
            {
                "packet_id": "stage15_probe_reasoning_0001",
                "title": "Contractor estimate workflow demand",
                "summary": "Research indicates demand for contractor proposal and estimate generation support.",
                "tags": ["contractor", "proposal", "estimate"],
                "metadata": {
                    "refinement_mode": "reasoning"
                },
            }
        )
    )

    results.append(
        run_research_command(
            {
                "packet_id": "stage15_probe_narrative_0001",
                "title": "Louisville GIS parcel workflow demand",
                "summary": "Research indicates demand for parcel lookup, zoning context, and GIS mapping support.",
                "tags": ["louisville", "gis", "parcel", "mapping"],
                "metadata": {
                    "refinement_mode": "narrative"
                },
            }
        )
    )

    results.append(
        run_research_command(
            {
                "packet_id": "stage15_probe_dual_0001",
                "title": "Contractor quote workflow demand",
                "summary": "Research indicates demand for contractor quote, estimate, and proposal process support.",
                "tags": ["contractor", "quote", "proposal"],
                "metadata": {
                    "refinement_mode": "dual"
                },
            }
        )
    )

    return {
        "status": "stage15_probe_complete",
        "results": results,
    }


if __name__ == "__main__":
    print(run())