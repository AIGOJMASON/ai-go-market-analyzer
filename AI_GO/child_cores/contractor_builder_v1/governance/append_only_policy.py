"""
Append-only policy helpers for contractor_builder_v1.

This module declares which contractor-family modules must preserve append-only history
and provides helper functions for revision/supersession references.
"""

from __future__ import annotations

from typing import Optional, Set


APPEND_ONLY_MODULES: Set[str] = {
    "change",
    "decision_log",
    "risk_register",
    "assumption_log",
    "comply",
    "report",
}


def module_requires_append_only(module_id: str) -> bool:
    """
    Return True if the module is governed by append-only rules.
    """
    return module_id in APPEND_ONLY_MODULES


def assert_append_only_module(module_id: str) -> None:
    """
    Raise ValueError if the module is not declared append-only.
    """
    if module_id not in APPEND_ONLY_MODULES:
        raise ValueError(
            f"Module '{module_id}' is not declared append-only in contractor governance."
        )


def build_supersedes_link(prior_id: Optional[str]) -> Optional[str]:
    """
    Return a lawful supersedes reference for revision-style records.
    """
    return prior_id or None