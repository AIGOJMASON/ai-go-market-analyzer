# AI_GO/child_cores/contractor_builder_v1/comply/jurisdiction_registry.py

"""
Minimal jurisdiction rules.
Expand over time — keep deterministic.
"""

JURISDICTION_RULES = {
    "default": {
        "permits_required": ["building"],
        "inspections_required": ["final"],
        "codes": {
            "electrical": ["NEC compliance required"],
            "structural": ["IBC compliance required"],
        },
    },
    "IN": {  # Indiana example
        "permits_required": ["building", "electrical"],
        "inspections_required": ["rough_in", "final"],
        "codes": {
            "electrical": ["NEC 2020"],
            "structural": ["IBC 2018"],
        },
    },
}


def get_jurisdiction_rules(jurisdiction: str):
    return JURISDICTION_RULES.get(jurisdiction, JURISDICTION_RULES["default"])