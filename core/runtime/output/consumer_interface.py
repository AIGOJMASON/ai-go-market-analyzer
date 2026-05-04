from __future__ import annotations

from typing import Any, Dict

from .consumer_profiles import CONSUMER_PROFILES
from .field_policy import FIELD_POLICY
from .render_policy import RENDER_POLICY
from .watcher_interface import validate_output


def validate_consumer(consumer_name: str) -> Dict[str, Any]:
    if consumer_name not in CONSUMER_PROFILES:
        return {
            "ok": False,
            "reason": "unknown_consumer",
            "consumer": consumer_name,
        }

    return {"ok": True}


def shape_for_consumer(artifact: Dict[str, Any], consumer_name: str) -> Dict[str, Any]:
    consumer_result = validate_consumer(consumer_name)
    if not consumer_result["ok"]:
        raise ValueError(f"Invalid consumer: {consumer_result}")

    output_result = validate_output(artifact)
    if not output_result["ok"]:
        raise ValueError(f"Artifact failed Stage 30 validation: {output_result}")

    allowed_fields = FIELD_POLICY[consumer_name]
    shaped = {field: artifact[field] for field in allowed_fields if field in artifact}

    render_mode = CONSUMER_PROFILES[consumer_name]["render_mode"]
    render_rule = RENDER_POLICY[render_mode]

    if render_rule["allow_full_artifact"]:
        return shaped

    return shaped


def get_consumer_view(artifact: Dict[str, Any], consumer_name: str) -> Dict[str, Any]:
    return shape_for_consumer(artifact, consumer_name)