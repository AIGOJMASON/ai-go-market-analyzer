# AI_GO/child_cores/contractor_builder_v1/comply/permit_runtime.py

from typing import List, Dict, Any
from .comply_schema import build_permit_record
from .jurisdiction_registry import get_jurisdiction_rules


def generate_required_permits(project_id: str, jurisdiction: str) -> List[Dict[str, Any]]:
    rules = get_jurisdiction_rules(jurisdiction)

    permits = []
    for permit_type in rules["permits_required"]:
        permits.append(
            build_permit_record(
                project_id=project_id,
                permit_type=permit_type,
                jurisdiction=jurisdiction,
                required=True,
                status="pending",
                blocking=True,
            )
        )

    return permits