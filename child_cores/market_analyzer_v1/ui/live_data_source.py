from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


_LIVE_STYLE_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "LIVE-DATA-001",
        "title": "Positive necessity rebound case",
        "source_type": "operator_refresh",
        "observed_at": "2026-03-20T16:00:00Z",
        "macro_context": {
            "headline": "Energy rebound after necessity shock",
            "macro_bias": "supportive",
        },
        "event_signal": {
            "event_id": "EVT-ENERGY-REBOUND-001",
            "event_type": "confirmed_shock",
            "event_theme": "energy_rebound",
            "confirmed": True,
            "propagation": "contained_but_tradeable",
        },
        "candidates": [
            {
                "symbol": "XLE",
                "sector": "energy",
                "necessity_qualified": True,
                "rebound_confirmed": True,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": "medium",
            }
        ],
        "operator_notes": "Positive live-style case for dashboard validation.",
    },
    {
        "case_id": "LIVE-DATA-002",
        "title": "Negative non-necessity case",
        "source_type": "operator_refresh",
        "observed_at": "2026-03-20T16:05:00Z",
        "macro_context": {
            "headline": "Consumer tech bounce without necessity qualification",
            "macro_bias": "mixed",
        },
        "event_signal": {
            "event_id": "EVT-TECH-BOUNCE-001",
            "event_type": "confirmed_shock",
            "event_theme": "tech_bounce",
            "confirmed": True,
            "propagation": "contained_but_non_necessity",
        },
        "candidates": [
            {
                "symbol": "QQQ",
                "sector": "technology",
                "necessity_qualified": False,
                "rebound_confirmed": True,
                "entry_signal": "gap reclaim",
                "exit_signal": "intraday extension",
                "confidence": "low",
            }
        ],
        "operator_notes": "Negative case. Should reject downstream.",
    },
]


def list_live_style_cases() -> List[Dict[str, Any]]:
    return [deepcopy(case) for case in _LIVE_STYLE_CASES]


def get_live_style_case(case_id: str) -> Dict[str, Any]:
    for case in _LIVE_STYLE_CASES:
        if case["case_id"] == case_id:
            return deepcopy(case)
    raise KeyError(f"Unknown live-style case: {case_id}")


def get_default_live_style_case() -> Dict[str, Any]:
    return deepcopy(_LIVE_STYLE_CASES[0])