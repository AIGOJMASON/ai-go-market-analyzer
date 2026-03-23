from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional


try:
    from core.shared.ids import make_id  # type: ignore
except Exception:
    def make_id(prefix: str = "WR-RESEARCH-PACKET") -> str:
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{prefix}-{stamp}"


try:
    from core.shared.timestamps import utc_now_iso  # type: ignore
except Exception:
    def utc_now_iso() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


try:
    from core.shared.io_utils import write_json  # type: ignore
except Exception:
    def write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


try:
    from core.shared.paths import get_project_root  # type: ignore
except Exception:
    def get_project_root() -> Path:
        return Path(__file__).resolve().parents[3]


RESEARCH_PACKET_PREFIX = "WR-RESEARCH-PACKET"
PACKET_SUBDIR = Path("packets") / "research"


def build_research_packet(
    intake_record: Dict[str, Any],
    screening_result: Dict[str, Any],
    trust_result: Dict[str, Any],
    *,
    packet_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the canonical in-memory research packet.

    RESEARCH_CORE owns packet shape.
    Runtime may call this, but runtime does not define the packet schema.
    """
    resolved_packet_id = packet_id or make_id(RESEARCH_PACKET_PREFIX)

    title = intake_record.get("title") or intake_record.get("summary") or "Research Packet"
    summary = intake_record.get("summary") or title
    source_refs = intake_record.get("source_refs") or []
    scope = intake_record.get("scope") or "core"
    tags = intake_record.get("tags") or ["research"]

    packet: Dict[str, Any] = {
        "packet_id": resolved_packet_id,
        "packet_type": "research_packet",
        "issuing_authority": "RESEARCH_CORE",
        "created_at": utc_now_iso(),
        "title": title,
        "summary": summary,
        "source_refs": source_refs,
        "scope": scope,
        "tags": tags,
        "intake_record": deepcopy(intake_record),
        "screening_result": deepcopy(screening_result),
        "trust_result": deepcopy(trust_result),
    }
    return packet


def packet_filename(packet: Dict[str, Any]) -> str:
    packet_id = str(packet["packet_id"])
    slug_source = packet.get("title") or packet.get("summary") or "research-packet"
    slug = _slugify(slug_source)
    return f"{packet_id}__{slug}.json"


def persist_research_packet(
    packet: Dict[str, Any],
    *,
    root_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Persist a research packet under AI_GO/packets/research/.

    RESEARCH_CORE owns persistence for research packet artifacts.
    """
    project_root = root_path or get_project_root()
    packet_dir = project_root / PACKET_SUBDIR
    packet_dir.mkdir(parents=True, exist_ok=True)

    path = packet_dir / packet_filename(packet)
    write_json(path, packet)

    return {
        "status": "persisted",
        "packet_id": packet["packet_id"],
        "packet_path": str(path),
        "packet_dir": str(packet_dir),
        "written_at": utc_now_iso(),
    }


def _slugify(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = []

    for ch in text:
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in {" ", "-", "_"}:
            cleaned.append("_")

    slug = "".join(cleaned).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")

    return slug or "research_packet"