from __future__ import annotations

from typing import Dict, Set


CURRENT_CONSUMPTION_POLICY_VERSION = "stage29.v1"
ALLOWED_UPSTREAM_DISTRIBUTION_POLICY_VERSIONS = {"stage28.v2"}


CONSUMER_PROFILES: Dict[str, Dict[str, Set[str] | str]] = {
    "pm_core_reader": {
        "allowed_requesting_surfaces": {"pm_core"},
        "allowed_targets": {
            "louisville_gis_core",
            "proposal_builder_core",
            "white_raven_university_core",
            "rosetta_writing_core",
        },
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "latest_n_records", "refs_only", "summary_stub"},
        "allowed_transformations": {"pm_planning_brief"},
        "allowed_packet_classes": {"continuity_strategy_packet"},
        "output_shape_mode": "pm_brief",
    },
    "strategy_reader": {
        "allowed_requesting_surfaces": {"strategy_layer"},
        "allowed_targets": {
            "louisville_gis_core",
            "proposal_builder_core",
            "white_raven_university_core",
            "rosetta_writing_core",
        },
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "latest_n_records", "refs_only", "summary_stub"},
        "allowed_transformations": {"strategy_signal_packet"},
        "allowed_packet_classes": {"continuity_strategy_packet"},
        "output_shape_mode": "strategy_signal",
    },
    "child_core_reader": {
        "allowed_requesting_surfaces": {"child_core_reader"},
        "allowed_targets": {
            "louisville_gis_core",
            "proposal_builder_core",
            "white_raven_university_core",
            "rosetta_writing_core",
        },
        "allowed_scopes": {"child_core"},
        "allowed_views": {"latest_record", "refs_only"},
        "allowed_transformations": {"child_core_context_packet"},
        "allowed_packet_classes": {"continuity_strategy_packet"},
        "output_shape_mode": "child_context",
    },
}


def is_registered_profile(profile: str) -> bool:
    return profile in CONSUMER_PROFILES


def is_allowed_requesting_surface(profile: str, requesting_surface: str) -> bool:
    return requesting_surface in CONSUMER_PROFILES.get(profile, {}).get("allowed_requesting_surfaces", set())


def is_allowed_target(profile: str, target: str) -> bool:
    return target in CONSUMER_PROFILES.get(profile, {}).get("allowed_targets", set())


def is_allowed_scope(profile: str, scope: str) -> bool:
    return scope in CONSUMER_PROFILES.get(profile, {}).get("allowed_scopes", set())


def is_allowed_view(profile: str, view: str) -> bool:
    return view in CONSUMER_PROFILES.get(profile, {}).get("allowed_views", set())


def is_allowed_transformation(profile: str, transformation_type: str) -> bool:
    return transformation_type in CONSUMER_PROFILES.get(profile, {}).get("allowed_transformations", set())


def is_allowed_packet_class(profile: str, packet_class: str) -> bool:
    return packet_class in CONSUMER_PROFILES.get(profile, {}).get("allowed_packet_classes", set())


def is_allowed_upstream_distribution_policy_version(version: str) -> bool:
    return version in ALLOWED_UPSTREAM_DISTRIBUTION_POLICY_VERSIONS


def get_output_shape_mode(profile: str) -> str:
    value = CONSUMER_PROFILES.get(profile, {}).get("output_shape_mode", "strategy_signal")
    return str(value)