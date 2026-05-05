# AI_GO/child_cores/contractor_builder_v1/comply/code_lookup_runtime.py

from typing import Dict, Any
from .jurisdiction_registry import get_jurisdiction_rules
from .comply_schema import build_code_lookup_result


def lookup_code(jurisdiction: str, category: str) -> Dict[str, Any]:
    rules = get_jurisdiction_rules(jurisdiction)
    codes = rules.get("codes", {}).get(category, [])

    return build_code_lookup_result(
        jurisdiction=jurisdiction,
        code_category=category,
        requirements=codes,
    )