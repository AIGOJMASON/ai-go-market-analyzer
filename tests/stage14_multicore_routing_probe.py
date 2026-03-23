from __future__ import annotations

from core.runtime.router import run_research_command


def run() -> dict:
    """
    Stage 14 probe set:
    - one clean contractor_proposals route
    - one clean louisville_gis route
    - one unresolved route that should land in unresolved queue
    """
    results = []

    results.append(
        run_research_command(
            {
                "packet_id": "stage14_probe_contractors_0001",
                "title": "Contractor proposal workflow demand",
                "summary": "Research indicates demand for contractor estimates, quoting, and proposal generation support.",
                "tags": ["contractor", "proposal", "estimate", "workflow"],
            }
        )
    )

    results.append(
        run_research_command(
            {
                "packet_id": "stage14_probe_gis_0001",
                "title": "Louisville parcel and zoning research demand",
                "summary": "Research indicates demand for parcel lookup, zoning context, and GIS mapping workflows in Louisville.",
                "tags": ["louisville", "gis", "parcel", "zoning", "mapping"],
            }
        )
    )

    results.append(
        run_research_command(
            {
                "packet_id": "stage14_probe_unresolved_0001",
                "title": "General local business operations demand",
                "summary": "Research indicates generic local workflow demand but does not justify a clear GIS or contractor proposal route.",
                "tags": ["local", "business", "workflow"],
            }
        )
    )

    return {
        "status": "stage14_probe_complete",
        "results": results,
    }


if __name__ == "__main__":
    print(run())