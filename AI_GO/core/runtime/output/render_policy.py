from __future__ import annotations

RENDER_POLICY = {
    "summary_only": {
        "include_fields": "policy_controlled",
        "allow_full_artifact": False,
    },
    "summary_with_refs": {
        "include_fields": "policy_controlled",
        "allow_full_artifact": False,
    },
    "closed_artifact": {
        "include_fields": "policy_controlled",
        "allow_full_artifact": True,
    },
}