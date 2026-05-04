# AI_GO/api/pre_interface_smi.py
from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from AI_GO.core.continuity.smi_write_path import (
        build_continuity_key,
        record_accepted_event,
    )
except ImportError:
    from core.continuity.smi_write_path import (  # type: ignore
        build_continuity_key,
        record_accepted_event,
    )


PASS_STATUSES = {"pass", "passed", "accepted", "ok", "success"}


def _watcher_passed(watcher_receipt: Dict[str, Any]) -> bool:
    if not isinstance(watcher_receipt, dict):
        return False

    for key in ("watcher_status", "validation_status", "status", "closeout_status"):
        value = watcher_receipt.get(key)
        if value and str(value).strip().lower() in PASS_STATUSES:
            return True

    nested_receipt = watcher_receipt.get("receipt")
    if isinstance(nested_receipt, dict):
        for key in ("watcher_status", "validation_status", "status", "closeout_status"):
            value = nested_receipt.get(key)
            if value and str(value).strip().lower() in PASS_STATUSES:
                return True

    return False


def _extract_symbol(system_view: Dict[str, Any]) -> Optional[str]:
    recommendation_panel = system_view.get("recommendation_panel")
    if isinstance(recommendation_panel, dict):
        items = recommendation_panel.get("items")
        if not isinstance(items, list):
            items = recommendation_panel.get("recommendations")

        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                symbol = first.get("symbol")
                if symbol:
                    return str(symbol)

    case_panel = system_view.get("case_panel")
    if isinstance(case_panel, dict):
        symbol = case_panel.get("symbol")
        if symbol:
            return str(symbol)

    runtime_panel = system_view.get("runtime_panel")
    if isinstance(runtime_panel, dict):
        symbol = runtime_panel.get("symbol")
        if symbol:
            return str(symbol)

    market_panel = system_view.get("market_panel")
    if isinstance(market_panel, dict):
        symbol = market_panel.get("symbol")
        if symbol:
            return str(symbol)

    return None


def _extract_event_theme(system_view: Dict[str, Any]) -> Optional[str]:
    for panel_key in ("runtime_panel", "market_panel", "refinement_panel", "cognition_panel"):
        panel = system_view.get(panel_key)
        if not isinstance(panel, dict):
            continue

        for key in ("event_theme", "theme", "pattern_class", "signal"):
            value = panel.get(key)
            if value:
                return str(value)

    return None


def record_pre_interface_continuity(
    *,
    watcher_receipt: Dict[str, Any],
    system_view: Dict[str, Any],
    core_id: str = "market_analyzer_v1",
) -> Dict[str, Any]:
    if not isinstance(watcher_receipt, dict):
        return {
            "status": "rejected",
            "reason": "watcher_receipt_must_be_dict",
        }

    if not isinstance(system_view, dict):
        return {
            "status": "rejected",
            "reason": "system_view_must_be_dict",
        }

    if not _watcher_passed(watcher_receipt):
        return {
            "status": "rejected",
            "reason": "watcher_receipt_not_passed",
        }

    symbol = _extract_symbol(system_view)
    event_theme = _extract_event_theme(system_view)

    case_panel = system_view.get("case_panel")
    case_id = case_panel.get("case_id") if isinstance(case_panel, dict) else None

    continuity_key = build_continuity_key(
        source_surface=core_id,
        event_class="interface_exposure_verified",
        symbol=symbol,
        event_theme=event_theme,
    )

    continuity_event = {
        "event_class": "interface_exposure_verified",
        "source_surface": core_id,
        "continuity_key": continuity_key,
        "case_id": case_id,
        "symbol": symbol,
        "event_theme": event_theme,
        "watcher_validation_id": (
            watcher_receipt.get("validation_id")
            or watcher_receipt.get("watcher_validation_id")
            or watcher_receipt.get("receipt_id")
            or (
                watcher_receipt.get("receipt", {}).get("validation_id")
                if isinstance(watcher_receipt.get("receipt"), dict)
                else None
            )
            or (
                watcher_receipt.get("receipt", {}).get("watcher_validation_id")
                if isinstance(watcher_receipt.get("receipt"), dict)
                else None
            )
            or (
                watcher_receipt.get("receipt", {}).get("receipt_id")
                if isinstance(watcher_receipt.get("receipt"), dict)
                else None
            )
        ),
    }

    result = record_accepted_event(continuity_event)

    return {
        "status": "recorded",
        "continuity_event_id": result["event_id"],
        "continuity_key": result["continuity_key"],
        "timestamp": result["timestamp"],
        "state_path": result["state_path"],
        "ledger_path": result["ledger_path"],
    }


def record_pre_interface_exposure(
    system_view: Dict[str, Any],
    watcher_receipt: Dict[str, Any],
    core_id: str = "market_analyzer_v1",
) -> Dict[str, Any]:
    return record_pre_interface_continuity(
        watcher_receipt=watcher_receipt,
        system_view=system_view,
        core_id=core_id,
    )