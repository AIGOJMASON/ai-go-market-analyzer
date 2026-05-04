from __future__ import annotations

from typing import Any, Dict, List


def safe_str(value: Any) -> str:
    return str(value or "").strip()


def safe_lower(value: Any) -> str:
    return safe_str(value).lower()


def safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []