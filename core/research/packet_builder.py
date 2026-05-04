from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json


RESEARCH_PACKET_BUILDER_VERSION = "northstar_research_packet_builder_v1"
MUTATION_CLASS = "source_signal_persistence"
PERSISTENCE_TYPE = "research_packet"


AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_project_truth": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "research_packet_source_signal_only",
}


@dataclass(frozen=True)
class ResearchPacket:
    packet_id: str
    packet_type: str
    issuing_authority: str
    created_at: str
    title: str
    summary: str
    source_refs: list[dict[str, Any]]
    scope: dict[str, Any]
    tags: list[str]
    intake_record: dict[str, Any]
    screening_result: dict[str, Any]
    trust_result: dict[str, Any]
    persistence_type: str
    mutation_class: str
    advisory_only: bool
    authority_metadata: dict[str, Any]
    sealed: bool


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized["artifact_type"] = "research_packet"
    normalized["artifact_version"] = RESEARCH_PACKET_BUILDER_VERSION
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    normalized["pm_authority_mutation_allowed"] = False
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_packet(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


class ResearchPacketBuilder:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2]
        self.packet_dir = self.root / "packets" / "research"

    def _timestamp(self) -> str:
        return _utc_now_iso()

    def build_packet(
        self,
        *,
        title: str,
        summary: str,
        intake_record: Dict[str, Any],
        screening_result: Dict[str, Any],
        trust_result: Dict[str, Any],
        source_refs: Optional[list[dict[str, Any]]] = None,
        scope: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        packet_type: str = "research_packet",
        issuing_authority: str = "RESEARCH_CORE",
    ) -> Dict[str, Any]:
        packet = ResearchPacket(
            packet_id=f"AI-GO-RESEARCH-{uuid4().hex[:12].upper()}",
            packet_type=_safe_str(packet_type) or "research_packet",
            issuing_authority=_safe_str(issuing_authority) or "RESEARCH_CORE",
            created_at=self._timestamp(),
            title=_safe_str(title),
            summary=_safe_str(summary),
            source_refs=[
                item
                for item in _safe_list(source_refs)
                if isinstance(item, dict)
            ],
            scope=_safe_dict(scope),
            tags=[
                _safe_str(item)
                for item in _safe_list(tags)
                if _safe_str(item)
            ],
            intake_record=_safe_dict(intake_record),
            screening_result=_safe_dict(screening_result),
            trust_result=_safe_dict(trust_result),
            persistence_type=PERSISTENCE_TYPE,
            mutation_class=MUTATION_CLASS,
            advisory_only=True,
            authority_metadata=dict(AUTHORITY_METADATA),
            sealed=True,
        )

        return _normalize_packet(asdict(packet))

    def validate_packet(self, packet: Dict[str, Any]) -> list[str]:
        errors: list[str] = []

        required = [
            "packet_id",
            "packet_type",
            "issuing_authority",
            "created_at",
            "title",
            "summary",
            "source_refs",
            "scope",
            "tags",
            "intake_record",
            "screening_result",
            "trust_result",
            "persistence_type",
            "mutation_class",
            "advisory_only",
        ]

        for field_name in required:
            if field_name not in packet:
                errors.append(f"missing_required_field:{field_name}")

        if packet.get("mutation_class") != MUTATION_CLASS:
            errors.append("invalid_mutation_class")

        if packet.get("advisory_only") is not True:
            errors.append("research_packet_must_be_advisory_only")

        return errors

    def persist_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        normalized = _normalize_packet(packet)
        errors = self.validate_packet(normalized)

        if errors:
            return {
                "status": "rejected",
                "errors": errors,
                "packet": normalized,
            }

        packet_id = _safe_str(normalized.get("packet_id"))
        if not packet_id:
            raise ValueError("packet_id is required")

        path = self.packet_dir / f"{packet_id}.json"
        written_path = _governed_write(path, normalized)

        return {
            "status": "persisted",
            "packet_id": packet_id,
            "packet_path": written_path,
            "packet": normalized,
        }

    def build_and_persist_packet(
        self,
        *,
        title: str,
        summary: str,
        intake_record: Dict[str, Any],
        screening_result: Dict[str, Any],
        trust_result: Dict[str, Any],
        source_refs: Optional[list[dict[str, Any]]] = None,
        scope: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        packet_type: str = "research_packet",
        issuing_authority: str = "RESEARCH_CORE",
    ) -> Dict[str, Any]:
        packet = self.build_packet(
            title=title,
            summary=summary,
            intake_record=intake_record,
            screening_result=screening_result,
            trust_result=trust_result,
            source_refs=source_refs,
            scope=scope,
            tags=tags,
            packet_type=packet_type,
            issuing_authority=issuing_authority,
        )
        return self.persist_packet(packet)


def build_research_packet(**kwargs: Any) -> Dict[str, Any]:
    return ResearchPacketBuilder().build_packet(**kwargs)


def persist_research_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    return ResearchPacketBuilder().persist_packet(packet)


def build_and_persist_research_packet(**kwargs: Any) -> Dict[str, Any]:
    return ResearchPacketBuilder().build_and_persist_packet(**kwargs)