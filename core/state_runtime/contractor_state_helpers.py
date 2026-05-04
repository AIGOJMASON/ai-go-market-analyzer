from __future__ import annotations

from typing import Any, Dict, List, Optional


def safe_str(value: Any) -> str:
    return str(value or "").strip()


def safe_lower(value: Any) -> str:
    return safe_str(value).lower()


def safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def find_phase(
    *,
    phase_id: str,
    phase_instances: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    clean_phase_id = safe_str(phase_id)

    for instance in phase_instances:
        if safe_str(instance.get("phase_id")) == clean_phase_id:
            return dict(instance)

    return None