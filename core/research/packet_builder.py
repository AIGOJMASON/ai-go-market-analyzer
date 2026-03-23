from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


class ResearchPacketBuilder:
    """
    Builds validated research packets for downstream refinement.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2]
        self.packet_dir = self.root / "packets" / "research"
        self.packet_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def build_packet(
        self,
        intake_record: Dict[str, Any],
        screening_result: Dict[str, Any],
        trust_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        packet_id = f"AI-GO-RESEARCH-PACKET-{uuid4().hex[:12].upper()}"

        packet = {
            "packet_id": packet_id,
            "timestamp": self._timestamp(),
            "packet_type": "research_packet",
            "status": "validated",
            "title": intake_record.get("title"),
            "summary": intake_record.get("summary"),
            "signal_type": intake_record.get("signal_type"),
            "intake_record": intake_record,
            "screening_result": screening_result,
            "trust_result": trust_result,
            "source_material": intake_record.get("source_material", []),
            "source_metadata": intake_record.get("source_metadata", {}),
        }

        path = self.packet_dir / f"{packet_id}.json"
        path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

        packet["packet_path"] = str(path)
        return packet