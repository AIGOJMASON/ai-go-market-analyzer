
---

## FILE: `AI_GO/core/child_flow/continuity/continuity_registry.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


CURRENT_POLICY_VERSION = "stage26.v1"


@dataclass(frozen=True)
class ContinuityTarget:
    target_core: str
    allowed_scopes: Set[str]
    allowed_policy_versions: Set[str]


REGISTERED_TARGETS: Dict[str, ContinuityTarget] = {
    "louisville_gis_core": ContinuityTarget(
        target_core="louisville_gis_core",
        allowed_scopes={"child_core", "pm"},
        allowed_policy_versions={CURRENT_POLICY_VERSION},
    ),
    "proposal_builder_core": ContinuityTarget(
        target_core="proposal_builder_core",
        allowed_scopes={"child_core", "pm"},
        allowed_policy_versions={CURRENT_POLICY_VERSION},
    ),
    "white_raven_university_core": ContinuityTarget(
        target_core="white_raven_university_core",
        allowed_scopes={"child_core", "pm"},
        allowed_policy_versions={CURRENT_POLICY_VERSION},
    ),
    "rosetta_writing_core": ContinuityTarget(
        target_core="rosetta_writing_core",
        allowed_scopes={"child_core", "pm"},
        allowed_policy_versions={CURRENT_POLICY_VERSION},
    ),
}


REJECTION_CODES: Set[str] = {
    "structural_invalid",
    "lineage_broken",
    "scope_unlawful",
    "duplicate_event",
    "stale_event",
    "insufficient_signal",
    "policy_version_invalid",
    "entropy_block",
}


def is_registered_target(target_core: str) -> bool:
    return target_core in REGISTERED_TARGETS


def is_allowed_scope(target_core: str, continuity_scope: str) -> bool:
    target = REGISTERED_TARGETS.get(target_core)
    if target is None:
        return False
    return continuity_scope in target.allowed_scopes


def is_allowed_policy_version(target_core: str, version: str) -> bool:
    target = REGISTERED_TARGETS.get(target_core)
    if target is None:
        return False
    return version in target.allowed_policy_versions


def list_registered_targets() -> List[str]:
    return sorted(REGISTERED_TARGETS.keys())