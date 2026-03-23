"""
AI_GO/core/runtime/cli.py

Lawful command-line entry surface for the AI_GO runtime.

Purpose:
- parse external command input
- normalize it into a governed runtime request
- hand the request to the runtime router
- return structured status payloads

This module does not perform research logic, PM logic, or child-core execution.
It only parses and forwards commands into the runtime authority path.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .router import route_command


VALID_COMMANDS = {
    "research",
    "status",
    "help",
}


def _build_help_payload() -> Dict[str, Any]:
    return {
        "status": "ok",
        "surface": "core.runtime.cli",
        "command": "help",
        "available_commands": [
            "research <query>",
            "status",
            "help",
        ],
    }


def _normalize_command(args: Sequence[str]) -> Dict[str, Any]:
    """
    Convert raw argv-style input into a governed command payload.
    """
    if not args:
        return {
            "command": "help",
            "payload": {},
        }

    command = str(args[0]).strip().lower()

    if command not in VALID_COMMANDS:
        raise ValueError(f"unknown command: {command}")

    if command == "research":
        query_parts = [str(part).strip() for part in args[1:] if str(part).strip()]
        if not query_parts:
            raise ValueError("research command requires a query")
        return {
            "command": "research",
            "payload": {
                "query": " ".join(query_parts),
            },
        }

    if command == "status":
        return {
            "command": "status",
            "payload": {},
        }

    return {
        "command": "help",
        "payload": {},
    }


def run_cli(args: Sequence[str]) -> Dict[str, Any]:
    """
    Main runtime CLI surface.

    Args:
        args: command-line arguments excluding the executable name.

    Returns:
        Structured runtime response payload.
    """
    normalized = _normalize_command(args)
    command = normalized["command"]

    if command == "help":
        return _build_help_payload()

    routed_result = route_command(
        command=command,
        payload=normalized["payload"],
    )

    return {
        "status": "ok",
        "surface": "core.runtime.cli",
        "command": command,
        "result": routed_result,
    }