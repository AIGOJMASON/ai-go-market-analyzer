from __future__ import annotations

from typing import Dict, Set


CURRENT_MUTATION_POLICY_VERSION = "stage27.v1"


REGISTERED_TARGETS: Dict[str, Dict[str, Set[str]]] = {
    "louisville_gis_core": {
        "allowed_scopes": {"child_core"},
        "allowed_upstream_intake_policy_versions": {"stage26.v1"},
        "allowed_mutation_policy_versions": {CURRENT_MUTATION_POLICY_VERSION},
    },
    "proposal_builder_core": {
        "allowed_scopes": {"child_core"},
        "allowed_upstream_intake_policy_versions": {"stage26.v1"},
        "allowed_mutation_policy_versions": {CURRENT_MUTATION_POLICY_VERSION},
    },
    "white_raven_university_core": {
        "allowed_scopes": {"child_core"},
        "allowed_upstream_intake_policy_versions": {"stage26.v1"},
        "allowed_mutation_policy_versions": {CURRENT_MUTATION_POLICY_VERSION},
    },
    "rosetta_writing_core": {
        "allowed_scopes": {"child_core"},
        "allowed_upstream_intake_policy_versions": {"stage26.v1"},
        "allowed_mutation_policy_versions": {CURRENT_MUTATION_POLICY_VERSION},
    },
}


def is_registered_target(target: str) -> bool:
    return target in REGISTERED_TARGETS


def is_allowed_scope(target: str, scope: str) -> bool:
    return scope in REGISTERED_TARGETS.get(target, {}).get("allowed_scopes", set())


def is_allowed_upstream_intake_policy_version(target: str, version: str) -> bool:
    return version in REGISTERED_TARGETS.get(target, {}).get(
        "allowed_upstream_intake_policy_versions",
        set(),
    )


def is_allowed_mutation_policy_version(target: str, version: str) -> bool:
    return version in REGISTERED_TARGETS.get(target, {}).get(
        "allowed_mutation_policy_versions",
        set(),
    )