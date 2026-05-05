"""
Conflict detector for contractor_builder_v1.

This module scans schedule blocks for advisory conflicts:
- date overlap
- same-resource overlap
- dependency timing problems

It reports conflicts only. It does not alter schedules or assignments.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from .router_schema import build_conflict_record


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _dates_overlap(
    start_a: str,
    end_a: str,
    start_b: str,
    end_b: str,
) -> bool:
    a_start = _parse_date(start_a)
    a_end = _parse_date(end_a)
    b_start = _parse_date(start_b)
    b_end = _parse_date(end_b)
    return a_start <= b_end and b_start <= a_end


def _dependency_violation(block: Dict[str, object], other: Dict[str, object]) -> bool:
    """
    Return True if block declares other.phase_id as a dependency but starts before
    other ends.
    """
    dependency_phase_ids = list(block.get("dependency_phase_ids", []))
    other_phase_id = str(other.get("phase_id", ""))

    if other_phase_id not in dependency_phase_ids:
        return False

    block_start = _parse_date(str(block.get("start_date", "")))
    other_end = _parse_date(str(other.get("end_date", "")))
    return block_start < other_end


def detect_schedule_conflicts(
    *,
    project_id: str,
    blocks: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    """
    Detect advisory conflicts across a set of schedule blocks.
    """
    conflicts: List[Dict[str, object]] = []
    seen_ids: set[str] = set()

    for index, primary in enumerate(blocks):
        for secondary in blocks[index + 1 :]:
            primary_block_id = str(primary.get("block_id", ""))
            secondary_block_id = str(secondary.get("block_id", ""))

            primary_phase_id = str(primary.get("phase_id", ""))
            secondary_phase_id = str(secondary.get("phase_id", ""))

            overlap = _dates_overlap(
                str(primary.get("start_date", "")),
                str(primary.get("end_date", "")),
                str(secondary.get("start_date", "")),
                str(secondary.get("end_date", "")),
            )

            same_resource = (
                bool(primary.get("resource_name"))
                and str(primary.get("resource_name", "")).strip().lower()
                == str(secondary.get("resource_name", "")).strip().lower()
            )

            if overlap and same_resource:
                conflict_id = f"conflict-{primary_block_id}-{secondary_block_id}-resource"
                if conflict_id not in seen_ids:
                    conflicts.append(
                        build_conflict_record(
                            project_id=project_id,
                            conflict_id=conflict_id,
                            conflict_type="Crew_Double_Booked",
                            primary_block_id=primary_block_id,
                            secondary_block_id=secondary_block_id,
                            primary_phase_id=primary_phase_id,
                            secondary_phase_id=secondary_phase_id,
                            severity="High",
                            notes="Same resource is assigned to overlapping blocks.",
                        )
                    )
                    seen_ids.add(conflict_id)

            if overlap and not same_resource:
                conflict_id = f"conflict-{primary_block_id}-{secondary_block_id}-overlap"
                if conflict_id not in seen_ids:
                    conflicts.append(
                        build_conflict_record(
                            project_id=project_id,
                            conflict_id=conflict_id,
                            conflict_type="Date_Overlap",
                            primary_block_id=primary_block_id,
                            secondary_block_id=secondary_block_id,
                            primary_phase_id=primary_phase_id,
                            secondary_phase_id=secondary_phase_id,
                            severity="Moderate",
                            notes="Two schedule blocks overlap in time.",
                        )
                    )
                    seen_ids.add(conflict_id)

            if _dependency_violation(primary, secondary):
                conflict_id = f"conflict-{primary_block_id}-{secondary_block_id}-dependency"
                if conflict_id not in seen_ids:
                    conflicts.append(
                        build_conflict_record(
                            project_id=project_id,
                            conflict_id=conflict_id,
                            conflict_type="Dependency_Violation",
                            primary_block_id=primary_block_id,
                            secondary_block_id=secondary_block_id,
                            primary_phase_id=primary_phase_id,
                            secondary_phase_id=secondary_phase_id,
                            severity="High",
                            notes="Primary block starts before dependency phase completes.",
                        )
                    )
                    seen_ids.add(conflict_id)

            if _dependency_violation(secondary, primary):
                conflict_id = f"conflict-{secondary_block_id}-{primary_block_id}-dependency"
                if conflict_id not in seen_ids:
                    conflicts.append(
                        build_conflict_record(
                            project_id=project_id,
                            conflict_id=conflict_id,
                            conflict_type="Dependency_Violation",
                            primary_block_id=secondary_block_id,
                            secondary_block_id=primary_block_id,
                            primary_phase_id=secondary_phase_id,
                            secondary_phase_id=primary_phase_id,
                            severity="High",
                            notes="Primary block starts before dependency phase completes.",
                        )
                    )
                    seen_ids.add(conflict_id)

    return conflicts