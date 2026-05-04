# AI_GO/child_cores/contractor_builder_v1/comply/comply_schema.py

from typing import Dict, Any, List


def build_permit_record(
    project_id: str,
    permit_type: str,
    jurisdiction: str,
    required: bool,
    status: str,
    blocking: bool,
) -> Dict[str, Any]:
    return {
        "record_type": "permit",
        "project_id": project_id,
        "permit_type": permit_type,
        "jurisdiction": jurisdiction,
        "required": required,
        "status": status,  # pending / approved / denied
        "blocking": blocking,
    }


def build_inspection_record(
    project_id: str,
    inspection_type: str,
    status: str,
    passed: bool,
    blocking: bool,
) -> Dict[str, Any]:
    return {
        "record_type": "inspection",
        "project_id": project_id,
        "inspection_type": inspection_type,
        "status": status,  # pending / scheduled / complete
        "passed": passed,
        "blocking": blocking,
    }


def build_code_lookup_result(
    jurisdiction: str,
    code_category: str,
    requirements: List[str],
) -> Dict[str, Any]:
    return {
        "record_type": "code_lookup",
        "jurisdiction": jurisdiction,
        "code_category": code_category,
        "requirements": requirements,
    }


def build_compliance_snapshot(
    project_id: str,
    permits: List[Dict[str, Any]],
    inspections: List[Dict[str, Any]],
) -> Dict[str, Any]:

    blocking_items = [
        p for p in permits if p.get("blocking") and p.get("status") != "approved"
    ] + [
        i for i in inspections if i.get("blocking") and not i.get("passed")
    ]

    return {
        "record_type": "compliance_snapshot",
        "project_id": project_id,
        "blocking": len(blocking_items) > 0,
        "blocking_count": len(blocking_items),
        "permits": permits,
        "inspections": inspections,
    }