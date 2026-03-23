from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from profiles import ChildCoreProfile
from policies import clamp_score


@dataclass(frozen=True)
class EngineAdapterResult:
    engine: str
    score: float
    status: str
    mode: str
    notes: str


def _packet_text(packet: Mapping[str, Any]) -> str:
    parts = [
        str(packet.get("packet_type", "")),
        str(packet.get("title", "")),
        str(packet.get("summary", "")),
        " ".join(str(x) for x in packet.get("tags", [])),
        str(packet.get("target_core_hint") or ""),
        str(packet.get("domain_hint") or ""),
        str(packet.get("notes") or ""),
    ]
    return " | ".join(part for part in parts if part)


def curved_mirror_adapter(packet: Mapping[str, Any], profile: ChildCoreProfile) -> EngineAdapterResult:
    text = _packet_text(packet).lower()
    score = 0.30

    if profile.domain_type.lower() in text:
        score += 0.15
    if any(keyword.lower() in text for keyword in profile.domain_keywords):
        score += 0.20
    if float(packet.get("confidence", 0.0)) >= 0.80:
        score += 0.15
    if len(packet.get("source_refs", [])) >= 2:
        score += 0.10
    if any(token in text for token in ["specific", "local", "louisville", "structured", "repeat"]):
        score += 0.05

    return EngineAdapterResult(
        engine="curved_mirror",
        score=clamp_score(score),
        status="invoked",
        mode="adapter",
        notes="Reasoning-weight estimation completed through bounded Curved Mirror adapter.",
    )


def rosetta_adapter(packet: Mapping[str, Any], profile: ChildCoreProfile) -> EngineAdapterResult:
    text = _packet_text(packet).lower()
    summary = str(packet.get("summary", ""))
    score = 0.25

    if len(summary) >= 80:
        score += 0.15
    if any(token in text for token in ["workflow", "clarity", "communication", "proposal", "brief", "usable"]):
        score += 0.20
    if profile.domain_type in {"proposals", "education", "narrative"}:
        score += 0.10
    if float(packet.get("confidence", 0.0)) >= 0.75:
        score += 0.10

    return EngineAdapterResult(
        engine="rosetta",
        score=clamp_score(score),
        status="invoked",
        mode="adapter",
        notes="Human-facing tempering estimation completed through bounded Rosetta adapter.",
    )


def invoke_refinement_engines(packet: Mapping[str, Any], profile: ChildCoreProfile) -> Dict[str, EngineAdapterResult]:
    curved = curved_mirror_adapter(packet, profile)
    rosetta = rosetta_adapter(packet, profile)
    return {
        "curved_mirror": curved,
        "rosetta": rosetta,
    }