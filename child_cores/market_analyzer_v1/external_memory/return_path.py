from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.EXTERNAL_MEMORY.return_path.return_path_runtime import build_return_packet
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.return_path.return_path_runtime import build_return_packet


def build_market_analyzer_return_packet(
    source_artifact: Dict[str, Any],
    source_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    return build_return_packet(
        source_artifact=source_artifact,
        source_receipt=source_receipt,
    )
