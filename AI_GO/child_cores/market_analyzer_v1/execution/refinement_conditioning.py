from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def apply_refinement_conditioning(ingress: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read-only conditioning pass.

    This module may shape emphasis for downstream interpretation,
    but it may not reweight, learn, mutate upstream truth, or
    create new authority.
    """
    conditioning = deepcopy(ingress.get("conditioning", {}))
    market_context = deepcopy(ingress.get("market_context", {}))
    event = deepcopy(ingress.get("event", {}))

    return {
        "conditioning_mode": "read_only",
        "macro_bias": deepcopy(ingress.get("macro_bias", {})),
        "event_priority": conditioning.get("event_priority", event.get("severity", "normal")),
        "liquidity_preference": conditioning.get("liquidity_preference", "high"),
        "holding_window_hours": conditioning.get("holding_window_hours", 48),
        "market_context_snapshot": market_context,
        "notes": deepcopy(conditioning.get("notes", [])),
    }