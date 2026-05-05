from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


class ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class ChildCoreProfile:
    child_core_id: str
    child_core_name: str
    status: str
    domain_type: str
    reasoning_coefficient: float
    human_tempering_coefficient: float
    core_fit_coefficient: float
    accepted_signal_patterns: List[str] = field(default_factory=list)
    rejected_signal_patterns: List[str] = field(default_factory=list)
    contamination_risks: List[str] = field(default_factory=list)
    preferred_refinement_order: List[str] = field(default_factory=lambda: ["curved_mirror", "rosetta"])
    last_updated: str = ""
    domain_keywords: List[str] = field(default_factory=list)
    task_biases: List[str] = field(default_factory=list)
    required_specificity_level: str = "medium"
    preferred_packet_types: List[str] = field(default_factory=list)
    hold_conditions: List[str] = field(default_factory=list)
    discard_conditions: List[str] = field(default_factory=list)
    conditioning_notes: Optional[str] = None
    max_contamination_penalty: float = 0.20
    profile_authority: str = "PM_CORE"
    receipt_ref: Optional[str] = None

    def coefficients(self) -> Dict[str, float]:
        return {
            "R": self.reasoning_coefficient,
            "H": self.human_tempering_coefficient,
            "C": self.core_fit_coefficient,
        }


DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
    "contractor_proposals_core": {
        "child_core_id": "contractor_proposals_core",
        "child_core_name": "contractor_proposals_core",
        "status": "active",
        "domain_type": "proposals",
        "reasoning_coefficient": 0.50,
        "human_tempering_coefficient": 0.15,
        "core_fit_coefficient": 0.35,
        "accepted_signal_patterns": [
            "estimate logic",
            "proposal workflow",
            "change order relevance",
            "contractor quoting process",
        ],
        "rejected_signal_patterns": [
            "generic inspirational content",
            "vague market commentary",
        ],
        "contamination_risks": ["narrative-only shaping without operational structure"],
        "preferred_refinement_order": ["curved_mirror", "rosetta"],
        "last_updated": "2026-03-17T00:00:00Z",
        "domain_keywords": ["proposal", "contractor", "estimate", "quote", "change order", "bid"],
        "preferred_packet_types": ["planning_brief", "research_packet"],
        "max_contamination_penalty": 0.25,
    },
    "louisville_gis_core": {
        "child_core_id": "louisville_gis_core",
        "child_core_name": "louisville_gis_core",
        "status": "active",
        "domain_type": "geospatial",
        "reasoning_coefficient": 0.55,
        "human_tempering_coefficient": 0.10,
        "core_fit_coefficient": 0.35,
        "accepted_signal_patterns": [
            "parcel data",
            "address intelligence",
            "map layer relevance",
            "Louisville location-specific data",
        ],
        "rejected_signal_patterns": [
            "generic business coaching",
            "non-local unsituated data",
        ],
        "contamination_risks": ["non-geospatial business content that only appears locally adjacent"],
        "preferred_refinement_order": ["curved_mirror", "rosetta"],
        "last_updated": "2026-03-17T00:00:00Z",
        "domain_keywords": ["louisville", "gis", "parcel", "zoning", "address", "mapping", "boundary"],
        "preferred_packet_types": ["planning_brief", "research_packet"],
        "max_contamination_penalty": 0.30,
    },
}


def _as_list(value: Any, field_name: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ProfileError(f"{field_name} must be a list of strings.")
    return value


def validate_profile_dict(data: Mapping[str, Any]) -> ChildCoreProfile:
    required = [
        "child_core_id", "child_core_name", "status", "domain_type",
        "reasoning_coefficient", "human_tempering_coefficient", "core_fit_coefficient",
        "accepted_signal_patterns", "rejected_signal_patterns", "contamination_risks",
        "preferred_refinement_order", "last_updated",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise ProfileError(f"Missing required profile fields: {', '.join(missing)}")

    coeff_sum = round(
        float(data["reasoning_coefficient"]) + float(data["human_tempering_coefficient"]) + float(data["core_fit_coefficient"]),
        4,
    )
    if abs(coeff_sum - 1.0) > 0.0001:
        raise ProfileError("Profile coefficients must sum to 1.00.")

    return ChildCoreProfile(
        child_core_id=str(data["child_core_id"]),
        child_core_name=str(data["child_core_name"]),
        status=str(data["status"]),
        domain_type=str(data["domain_type"]),
        reasoning_coefficient=float(data["reasoning_coefficient"]),
        human_tempering_coefficient=float(data["human_tempering_coefficient"]),
        core_fit_coefficient=float(data["core_fit_coefficient"]),
        accepted_signal_patterns=_as_list(data.get("accepted_signal_patterns"), "accepted_signal_patterns"),
        rejected_signal_patterns=_as_list(data.get("rejected_signal_patterns"), "rejected_signal_patterns"),
        contamination_risks=_as_list(data.get("contamination_risks"), "contamination_risks"),
        preferred_refinement_order=_as_list(data.get("preferred_refinement_order"), "preferred_refinement_order") or ["curved_mirror", "rosetta"],
        last_updated=str(data["last_updated"]),
        domain_keywords=_as_list(data.get("domain_keywords"), "domain_keywords"),
        task_biases=_as_list(data.get("task_biases"), "task_biases"),
        required_specificity_level=str(data.get("required_specificity_level", "medium")),
        preferred_packet_types=_as_list(data.get("preferred_packet_types"), "preferred_packet_types"),
        hold_conditions=_as_list(data.get("hold_conditions"), "hold_conditions"),
        discard_conditions=_as_list(data.get("discard_conditions"), "discard_conditions"),
        conditioning_notes=data.get("conditioning_notes"),
        max_contamination_penalty=float(data.get("max_contamination_penalty", 0.20)),
        profile_authority=str(data.get("profile_authority", "PM_CORE")),
        receipt_ref=data.get("receipt_ref"),
    )


class ProfileStore:
    def __init__(self, profiles: Optional[Mapping[str, Mapping[str, Any]]] = None) -> None:
        base = profiles or DEFAULT_PROFILES
        self._profiles: Dict[str, ChildCoreProfile] = {
            name: validate_profile_dict(profile) for name, profile in base.items()
        }

    def get(self, child_core_name: str) -> ChildCoreProfile:
        if child_core_name not in self._profiles:
            raise ProfileError(f"Unknown child-core profile: {child_core_name}")
        return self._profiles[child_core_name]

    def all(self) -> List[ChildCoreProfile]:
        return list(self._profiles.values())

    def active(self) -> List[ChildCoreProfile]:
        return [profile for profile in self._profiles.values() if profile.status == "active"]


def infer_fit_score(packet_text: str, profile: ChildCoreProfile) -> float:
    lowered = packet_text.lower()
    accepted_hits = sum(1 for pattern in (profile.accepted_signal_patterns + profile.domain_keywords) if pattern.lower() in lowered)
    rejected_hits = sum(1 for pattern in profile.rejected_signal_patterns if pattern.lower() in lowered)

    base = 0.20
    if accepted_hits:
        base += min(0.60, accepted_hits * 0.12)
    if rejected_hits:
        base -= min(0.35, rejected_hits * 0.10)

    packet_type_bonus = 0.0
    for packet_type in profile.preferred_packet_types:
        if packet_type.lower() in lowered:
            packet_type_bonus = 0.08
            break

    score = max(0.0, min(1.0, round(base + packet_type_bonus, 4)))
    return score


def contamination_penalty(packet_text: str, profile: ChildCoreProfile) -> float:
    lowered = packet_text.lower()
    hits = sum(1 for pattern in profile.contamination_risks if pattern.lower() in lowered)
    if not hits:
        return 0.0
    penalty = min(profile.max_contamination_penalty, hits * 0.10)
    return round(penalty, 4)