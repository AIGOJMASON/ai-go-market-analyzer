"""
Capacity detector for contractor_builder_v1.

This module creates advisory capacity posture summaries for named resources.
It does not assign crews or mutate schedules.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, List

from .router_schema import build_capacity_record


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _max_concurrency(blocks: List[Dict[str, object]]) -> int:
    """
    Compute a simple maximum concurrent block count for a resource.
    """
    events: List[tuple[date, int]] = []

    for block in blocks:
        start = _parse_date(str(block.get("start_date", "")))
        end = _parse_date(str(block.get("end_date", "")))
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda item: (item[0], -item[1]))

    current = 0
    maximum = 0
    for _, delta in events:
        current += delta
        if current > maximum:
            maximum = current

    return maximum


def detect_capacity_status(
    *,
    concurrent_block_count: int,
    capacity_limit: int,
) -> str:
    """
    Convert concurrent demand vs capacity into an advisory capacity status.
    """
    if capacity_limit <= 0:
        return "Overloaded"

    utilization = concurrent_block_count / capacity_limit

    if utilization <= 0.75:
        return "Healthy"
    if utilization <= 1.0:
        return "Watch"
    return "Overloaded"


def build_capacity_snapshot(
    *,
    project_id: str,
    blocks: List[Dict[str, object]],
    capacity_limits: Dict[str, int] | None = None,
) -> List[Dict[str, object]]:
    """
    Build capacity posture records grouped by resource_name.
    """
    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    limits = capacity_limits or {}
    records: List[Dict[str, object]] = []

    for block in blocks:
        resource_name = str(block.get("resource_name", "")).strip()
        if not resource_name:
            continue
        grouped[resource_name].append(block)

    for resource_name, resource_blocks in grouped.items():
        resource_type = str(resource_blocks[0].get("resource_type", ""))
        assigned_block_count = len(resource_blocks)
        concurrent_block_count = _max_concurrency(resource_blocks)
        capacity_limit = int(limits.get(resource_name, 1))
        capacity_status = detect_capacity_status(
            concurrent_block_count=concurrent_block_count,
            capacity_limit=capacity_limit,
        )

        records.append(
            build_capacity_record(
                project_id=project_id,
                snapshot_id=f"capacity-{project_id}-{resource_name}",
                resource_name=resource_name,
                resource_type=resource_type,
                assigned_block_count=assigned_block_count,
                concurrent_block_count=concurrent_block_count,
                capacity_limit=capacity_limit,
                capacity_status=capacity_status,
                notes="Advisory capacity posture only.",
            )
        )

    return records