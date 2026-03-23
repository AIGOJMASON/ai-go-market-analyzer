from __future__ import annotations

from typing import Dict, Optional, Set


CURRENT_DISTRIBUTION_POLICY_VERSION = "stage28.v2"


REGISTERED_TARGETS: Dict[str, Dict[str, Set[str]]] = {
    "louisville_gis_core": {
        "allowed_scopes": {"child_core"},
        "allowed_policy_versions": {CURRENT_DISTRIBUTION_POLICY_VERSION},
    },
    "proposal_builder_core": {
        "allowed_scopes": {"child_core"},
        "allowed_policy_versions": {CURRENT_DISTRIBUTION_POLICY_VERSION},
    },
    "white_raven_university_core": {
        "allowed_scopes": {"child_core"},
        "allowed_policy_versions": {CURRENT_DISTRIBUTION_POLICY_VERSION},
    },
    "rosetta_writing_core": {
        "allowed_scopes": {"child_core"},
        "allowed_policy_versions": {CURRENT_DISTRIBUTION_POLICY_VERSION},
    },
}


CONSUMER_PROFILES: Dict[str, Dict[str, object]] = {
    "pm_core_reader": {
        "allowed_requesting_surfaces": {"pm_core"},
        "allowed_targets": set(REGISTERED_TARGETS.keys()),
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "latest_n_records", "refs_only", "summary_stub"},
        "default_view": "summary_stub",
        "max_records": 5,
        "shape_mode": "full_bounded",
    },
    "strategy_reader": {
        "allowed_requesting_surfaces": {"strategy_layer"},
        "allowed_targets": set(REGISTERED_TARGETS.keys()),
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "latest_n_records", "refs_only", "summary_stub"},
        "default_view": "summary_stub",
        "max_records": 5,
        "shape_mode": "summary_stub",
    },
    "child_core_reader": {
        "allowed_requesting_surfaces": {"child_core_reader"},
        "allowed_targets": set(REGISTERED_TARGETS.keys()),
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "refs_only"},
        "default_view": "latest_record",
        "max_records": 1,
        "shape_mode": "refs_only",
    },
}


def is_registered_target(target: str) -> bool:
    return target in REGISTERED_TARGETS


def is_registered_profile(profile: str) -> bool:
    return profile in CONSUMER_PROFILES


def is_allowed_scope(target: str, scope: str) -> bool:
    return scope in REGISTERED_TARGETS.get(target, {}).get("allowed_scopes", set())


def is_allowed_policy_version(target: str, version: str) -> bool:
    return version in REGISTERED_TARGETS.get(target, {}).get("allowed_policy_versions", set())


def is_allowed_requesting_surface(profile: str, requesting_surface: str) -> bool:
    return requesting_surface in CONSUMER_PROFILES.get(profile, {}).get("allowed_requesting_surfaces", set())


def is_allowed_profile_target(profile: str, target: str) -> bool:
    return target in CONSUMER_PROFILES.get(profile, {}).get("allowed_targets", set())


def is_allowed_profile_scope(profile: str, scope: str) -> bool:
    return scope in CONSUMER_PROFILES.get(profile, {}).get("allowed_scopes", set())


def is_allowed_profile_view(profile: str, view: str) -> bool:
    return view in CONSUMER_PROFILES.get(profile, {}).get("allowed_views", set())


def get_profile_default_view(profile: str) -> Optional[str]:
    value = CONSUMER_PROFILES.get(profile, {}).get("default_view")
    return value if isinstance(value, str) else None


def get_profile_max_records(profile: str) -> int:
    value = CONSUMER_PROFILES.get(profile, {}).get("max_records", 1)
    return int(value)


def get_profile_shape_mode(profile: str) -> str:
    value = CONSUMER_PROFILES.get(profile, {}).get("shape_mode", "summary_stub")
    return str(value)