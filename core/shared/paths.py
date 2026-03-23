"""
AI_GO/core/shared/paths.py

Filesystem path helpers for AI_GO.

Purpose:
- provide stable root-relative paths
- prevent scattered hardcoded path logic
- give all layers a consistent path surface
"""

from __future__ import annotations

from pathlib import Path


def get_ai_go_root() -> Path:
    """
    Return the AI_GO project root.

    This file lives at:
        AI_GO/core/shared/paths.py

    Therefore:
        parents[2] == AI_GO/
    """
    return Path(__file__).resolve().parents[2]


def get_boot_dir() -> Path:
    return get_ai_go_root() / "boot"


def get_core_dir() -> Path:
    return get_ai_go_root() / "core"


def get_lib_dir() -> Path:
    return get_ai_go_root() / "lib"


def get_state_dir() -> Path:
    return get_ai_go_root() / "state"


def get_packets_dir() -> Path:
    return get_ai_go_root() / "packets"


def get_telemetry_dir() -> Path:
    return get_ai_go_root() / "telemetry"


def get_child_cores_dir() -> Path:
    return get_ai_go_root() / "child_cores"


def get_research_core_dir() -> Path:
    return get_ai_go_root() / "RESEARCH_CORE"


def get_pm_core_dir() -> Path:
    return get_ai_go_root() / "PM_CORE"


def get_engines_dir() -> Path:
    return get_ai_go_root() / "engines"