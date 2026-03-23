from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def build_receipt_trace_view(receipt_trace_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the receipt / trace layer view.
    """
    packet = deepcopy(receipt_trace_packet)

    return {
        "panel": "receipt_trace",
        "core_id": "market_analyzer_v1",
        "artifact_type": "receipt_trace_view",
        "upstream_receipt": deepcopy(packet.get("upstream_receipt")),
        "trace": deepcopy(packet.get("trace", {})),
        "source_artifact": packet.get("artifact_type"),
    }