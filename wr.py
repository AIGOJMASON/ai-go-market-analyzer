#!/usr/bin/env python3
"""
AI_GO/wr.py

Thin command-line wrapper for the AI_GO runtime.

Purpose:
- expose the first live command surface for AI_GO
- forward user input into the lawful runtime CLI layer
- keep the root entry point thin so authority remains inside core/runtime/

This file does not implement research logic directly.
It only forwards commands to core.runtime.cli.
"""

from __future__ import annotations

import json
import sys
from typing import Sequence

from core.runtime.cli import run_cli


def main(argv: Sequence[str] | None = None) -> int:
    """
    Execute the AI_GO CLI wrapper.

    Returns:
        int: process exit code
    """
    args = list(argv if argv is not None else sys.argv[1:])

    try:
        result = run_cli(args)
    except Exception as exc:  # pragma: no cover
        error_payload = {
            "status": "error",
            "entrypoint": "wr.py",
            "error_type": exc.__class__.__name__,
            "message": str(exc),
        }
        print(json.dumps(error_payload, indent=2))
        return 1

    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    elif result is not None:
        print(str(result))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())