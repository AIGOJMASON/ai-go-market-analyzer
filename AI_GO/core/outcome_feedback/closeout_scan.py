from __future__ import annotations

import json
from pathlib import Path


def _closeout_dir() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "receipts"
        / "market_analyzer_v1"
        / "closeout"
    )


def _has_symbol(artifact: dict) -> bool:
    direct_symbol = str(artifact.get("symbol", "")).strip()
    if direct_symbol:
        return True

    case_panel = artifact.get("case_panel", {})
    case_symbol = str(case_panel.get("symbol", "")).strip()
    if case_symbol:
        return True

    recommendation_panel = artifact.get("recommendation_panel", {})
    items = recommendation_panel.get("items", [])
    if items and isinstance(items[0], dict):
        rec_symbol = str(items[0].get("symbol", "")).strip()
        if rec_symbol:
            return True

    return False


def _has_reference_price(artifact: dict) -> bool:
    direct_price = artifact.get("reference_price")
    if direct_price is not None:
        return True

    market_panel = artifact.get("market_panel", {})
    for field in ("reference_price", "price_at_closeout"):
        if market_panel.get(field) is not None:
            return True

    recommendation_panel = artifact.get("recommendation_panel", {})
    items = recommendation_panel.get("items", [])
    if items and isinstance(items[0], dict):
        if items[0].get("entry") is not None:
            return True

    return False


def _has_event_theme(artifact: dict) -> bool:
    runtime_panel = artifact.get("runtime_panel", {})
    runtime_event_theme = str(runtime_panel.get("event_theme", "")).strip()
    if runtime_event_theme:
        return True

    market_panel = artifact.get("market_panel", {})
    market_event_theme = str(market_panel.get("event_theme", "")).strip()
    if market_event_theme:
        return True

    direct_expected = str(artifact.get("expected_behavior", "")).strip()
    if direct_expected:
        return True

    return False


def is_market_outcome_compatible(artifact: dict) -> bool:
    return (
        _has_symbol(artifact)
        and _has_reference_price(artifact)
        and _has_event_theme(artifact)
    )


def load_closeout_artifacts() -> list[dict]:
    closeout_dir = _closeout_dir()
    if not closeout_dir.exists():
        return []

    artifacts: list[dict] = []
    for path in sorted(closeout_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            payload["_artifact_path"] = str(path)
            artifacts.append(payload)

    return artifacts


def select_next_eligible_closeout(
    *,
    closeout_artifacts: list[dict],
    processed_closeout_ids: set[str],
) -> dict | None:
    for artifact in reversed(closeout_artifacts):
        closeout_id = str(artifact.get("closeout_id", "")).strip()
        closeout_status = str(artifact.get("closeout_status", "")).strip().lower()

        if not closeout_id:
            continue

        if closeout_status != "accepted":
            continue

        if closeout_id in processed_closeout_ids:
            continue

        if not is_market_outcome_compatible(artifact):
            continue

        return artifact

    return None