# AI_GO/child_cores/contractor_builder_v1/comply/snapshot_runtime.py

from typing import List, Dict, Any
from .comply_schema import build_compliance_snapshot


def build_snapshot(project_id: str, permits: List[Dict[str, Any]], inspections: List[Dict[str, Any]]) -> Dict[str, Any]:
    return build_compliance_snapshot(project_id, permits, inspections)