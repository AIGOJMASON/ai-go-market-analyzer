"""
Exposure profile runtime for contractor_builder_v1.

This module builds project exposure profiles that map project sensitivity by market
domain. Exposure is declared, not inferred magically.
"""

from __future__ import annotations

from typing import Dict, Any

from .oracle_schema import build_exposure_profile, validate_exposure_profile


def build_project_exposure_profile(
    *,
    exposure_profile_id: str,
    project_id: str,
    domain_exposure: Dict[str, str],
    weighting_notes: str = "",
) -> Dict[str, Any]:
    """
    Build and validate a canonical exposure profile.
    """
    profile = build_exposure_profile(
        exposure_profile_id=exposure_profile_id,
        project_id=project_id,
        domain_exposure=domain_exposure,
        weighting_notes=weighting_notes,
    )

    errors = validate_exposure_profile(profile)
    if errors:
        raise ValueError("Invalid exposure profile: " + "; ".join(errors))

    return profile