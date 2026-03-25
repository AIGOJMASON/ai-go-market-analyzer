from __future__ import annotations

from typing import Any, Dict

from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response


def build_operator_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the canonical single-surface operator dashboard payload.

    Internal runtime, refinement, and PM workflow artifacts may remain
    separately governed and separately receipted. Outwardly, the operator
    receives one unified system_view object.
    """
    response = build_market_analyzer_response(payload)
    return response.model_dump(by_alias=True, exclude_none=False)