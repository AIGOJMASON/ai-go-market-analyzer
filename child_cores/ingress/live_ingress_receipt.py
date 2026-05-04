from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_live_ingress_receipt(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_type": "live_ingress_receipt",
        "ingress_id": f"LIVE-INGRESS-{uuid4()}",
        "ingress_surface": packet.get("ingress_surface"),
        "packet_type": packet.get("packet_type"),
        "case_id": packet.get("case_id"),
        "parent_authority": packet.get("parent_authority"),
        "target_core": packet.get("target_core"),
        "handoff_status": "constructed",
        "timestamp": utc_now_iso(),
    }