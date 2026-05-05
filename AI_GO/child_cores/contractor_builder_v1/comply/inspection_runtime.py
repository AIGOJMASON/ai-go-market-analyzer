# AI_GO/child_cores/contractor_builder_v1/comply/inspection_runtime.py

from typing import List, Dict, Any
from .comply_schema import build_inspection_record
from .jurisdiction_registry import get_jurisdiction_rules


def generate_required_inspections(project_id: str, jurisdiction: str) -> List[Dict[str, Any]]:
    rules = get_jurisdiction_rules(jurisdiction)

    inspections = []
    for inspection_type in rules["inspections_required"]:
        inspections.append(
            build_inspection_record(
                project_id=project_id,
                inspection_type=inspection_type,
                status="pending",
                passed=False,
                blocking=True,
            )
        )

    return inspections