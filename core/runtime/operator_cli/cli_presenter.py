from __future__ import annotations

from typing import Any, Dict

from .cli_render_policy import CLI_RENDER_POLICY
from .cli_view_registry import CLI_VIEW_REGISTRY


def validate_cli_view(view_type: str) -> Dict[str, Any]:
    if view_type not in CLI_VIEW_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_cli_view",
            "view_type": view_type,
        }
    return {"ok": True}


def shape_cli_payload(view_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    view_result = validate_cli_view(view_type)
    if not view_result["ok"]:
        raise ValueError(f"Invalid CLI view: {view_result}")

    allowed_fields = CLI_RENDER_POLICY[view_type]
    return {field: payload[field] for field in allowed_fields if field in payload}


def render_cli_block(view_type: str, payload: Dict[str, Any]) -> str:
    shaped = shape_cli_payload(view_type, payload)

    if not shaped:
        raise ValueError("CLI payload shaped to empty output")

    lines = [f"[{view_type}]"]
    for key, value in shaped.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)