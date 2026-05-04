"""
engines.curved_mirror.prompts

Prompt-shaping helpers for the Curved Mirror engine.
These helpers structure reasoning-oriented refinement prompts without altering authority.
"""

from __future__ import annotations

from typing import Any, Dict


def build_reasoning_prompt(gated_input: Dict[str, Any]) -> Dict[str, str]:
    """
    Build a bounded reasoning prompt shape from a governed gated input.
    """
    summary = str(gated_input.get("summary", "")).strip()
    scope = str(gated_input.get("scope", "")).strip()
    target_engine = str(gated_input.get("target_engine", "")).strip()

    prompt_shape = (
        "Reasoning refinement input\n"
        f"Target engine: {target_engine}\n"
        f"Scope: {scope}\n"
        f"Summary: {summary}\n"
        "Task: extract bounded reasoning structure while preserving provenance."
    )

    return {
        "prompt_shape": prompt_shape,
    }