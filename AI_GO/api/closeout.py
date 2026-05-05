from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json


CLOSEOUT_MUTATION_CLASS = "closeout_artifact_persistence"
CLOSEOUT_PERSISTENCE_TYPE = "filesystem"
CLOSEOUT_ADVISORY_ONLY = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _closeout_dir() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "receipts"
        / "market_analyzer_v1"
        / "closeout"
    )


def _build_closeout_id(core_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid4().hex[:10]
    return f"closeout_{core_id}_{ts}_{suffix}"


def _classification_block() -> dict[str, Any]:
    return {
        "mutation_class": CLOSEOUT_MUTATION_CLASS,
        "persistence_type": CLOSEOUT_PERSISTENCE_TYPE,
        "advisory_only": CLOSEOUT_ADVISORY_ONLY,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> dict[str, Any]:
    return {
        "governed_persistence": True,
        "closeout_artifact": True,
        "can_execute": False,
        "can_mutate_operational_state": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }


def _normalize_system_view(
    *,
    system_view: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate = system_view or response_payload or {}
    return candidate if isinstance(candidate, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _safe_upper(value: Any) -> str:
    return _safe_str(value).upper()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_recommendation_item(system_view: dict[str, Any]) -> dict[str, Any]:
    recommendation_panel = _safe_dict(system_view.get("recommendation_panel"))

    items = recommendation_panel.get("items")
    if items is None:
        items = recommendation_panel.get("recommendations", [])

    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]

    return {}


def _derive_symbol(system_view: dict[str, Any]) -> str:
    direct_symbol = _safe_upper(system_view.get("symbol"))
    if direct_symbol:
        return direct_symbol

    case_panel = _safe_dict(system_view.get("case_panel"))
    case_symbol = _safe_upper(case_panel.get("symbol"))
    if case_symbol:
        return case_symbol

    market_panel = _safe_dict(system_view.get("market_panel"))
    market_symbol = _safe_upper(market_panel.get("symbol"))
    if market_symbol:
        return market_symbol

    live_event_panel = _safe_dict(system_view.get("live_event_panel"))
    live_symbol = _safe_upper(live_event_panel.get("symbol"))
    if live_symbol:
        return live_symbol

    operator_packet = _safe_dict(system_view.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    current_case_symbol = _safe_upper(current_case.get("symbol"))
    if current_case_symbol:
        return current_case_symbol

    rec_item = _first_recommendation_item(system_view)
    rec_symbol = _safe_upper(rec_item.get("symbol"))
    if rec_symbol:
        return rec_symbol

    watchlist_panel = _safe_dict(system_view.get("watchlist_panel"))
    source_symbol = _safe_upper(watchlist_panel.get("source_symbol"))
    if source_symbol:
        return source_symbol

    return ""


def _derive_reference_price(system_view: dict[str, Any]) -> float | int | None:
    for field in ("reference_price", "price_at_closeout", "price", "current_price"):
        value = system_view.get(field)
        if value is not None:
            return value

    market_panel = _safe_dict(system_view.get("market_panel"))
    for field in ("reference_price", "price_at_closeout", "price", "current_price"):
        value = market_panel.get(field)
        if value is not None:
            return value

    live_event_panel = _safe_dict(system_view.get("live_event_panel"))
    for field in ("reference_price", "price_at_closeout", "price", "current_price"):
        value = live_event_panel.get(field)
        if value is not None:
            return value

    operator_packet = _safe_dict(system_view.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    for field in ("reference_price", "price_at_closeout", "price", "current_price"):
        value = current_case.get(field)
        if value is not None:
            return value

    rec_item = _first_recommendation_item(system_view)
    for field in ("entry", "reference_price", "price_at_closeout", "price"):
        value = rec_item.get(field)
        if value is not None:
            return value

    return None


def _derive_request_id(system_view: dict[str, Any]) -> str:
    direct = _safe_str(system_view.get("request_id"))
    if direct:
        return direct

    case_panel = _safe_dict(system_view.get("case_panel"))
    case_id = _safe_str(case_panel.get("case_id"))
    if case_id:
        return case_id

    operator_packet = _safe_dict(system_view.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    current_request_id = _safe_str(current_case.get("request_id"))
    if current_request_id:
        return current_request_id

    return ""


def _derive_generated_at(system_view: dict[str, Any]) -> str:
    for field in ("board_generated_at", "generated_at", "observed_at"):
        value = _safe_str(system_view.get(field))
        if value:
            return value

    case_panel = _safe_dict(system_view.get("case_panel"))
    case_observed_at = _safe_str(case_panel.get("observed_at"))
    if case_observed_at:
        return case_observed_at

    operator_packet = _safe_dict(system_view.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    for field in ("observed_at", "generated_at"):
        value = _safe_str(current_case.get(field))
        if value:
            return value

    return ""


def _copy_case_panel(
    system_view: dict[str, Any],
    derived_symbol: str,
    derived_request_id: str,
    derived_generated_at: str,
) -> dict[str, Any] | None:
    case_panel = _safe_dict(system_view.get("case_panel"))

    allowed: dict[str, Any] = {}
    for field in ("case_id", "title", "symbol", "observed_at"):
        value = case_panel.get(field)
        if value is not None:
            allowed[field] = value

    if not allowed.get("case_id") and derived_request_id:
        allowed["case_id"] = derived_request_id

    if not allowed.get("symbol") and derived_symbol:
        allowed["symbol"] = derived_symbol

    if not allowed.get("observed_at") and derived_generated_at:
        allowed["observed_at"] = derived_generated_at

    return allowed or None


def _copy_runtime_panel(system_view: dict[str, Any]) -> dict[str, Any] | None:
    runtime_panel = _safe_dict(system_view.get("runtime_panel"))
    if not runtime_panel:
        return None

    allowed: dict[str, Any] = {}
    for field in ("market_regime", "event_theme", "macro_bias", "headline"):
        value = runtime_panel.get(field)
        if value is not None:
            allowed[field] = value

    return allowed or None


def _copy_market_panel(
    system_view: dict[str, Any],
    derived_symbol: str,
    derived_reference_price: float | int | None,
) -> dict[str, Any] | None:
    market_panel = _safe_dict(system_view.get("market_panel"))

    allowed: dict[str, Any] = {}
    for field in (
        "symbol",
        "market_regime",
        "event_theme",
        "macro_bias",
        "headline",
        "price",
        "reference_price",
        "price_at_closeout",
    ):
        value = market_panel.get(field)
        if value is not None:
            allowed[field] = value

    if not allowed.get("symbol") and derived_symbol:
        allowed["symbol"] = derived_symbol

    if allowed.get("reference_price") is None and derived_reference_price is not None:
        allowed["reference_price"] = derived_reference_price

    if allowed.get("price_at_closeout") is None and derived_reference_price is not None:
        allowed["price_at_closeout"] = derived_reference_price

    if allowed.get("price") is None and derived_reference_price is not None:
        allowed["price"] = derived_reference_price

    return allowed or None


def _copy_recommendation_panel(system_view: dict[str, Any]) -> dict[str, Any] | None:
    recommendation_panel = _safe_dict(system_view.get("recommendation_panel"))
    if not recommendation_panel:
        return None

    items = recommendation_panel.get("items")
    if items is None:
        items = recommendation_panel.get("recommendations", [])

    normalized_items: list[dict[str, Any]] = []

    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue

            normalized_item: dict[str, Any] = {}
            for field in ("symbol", "entry", "exit", "thesis", "state", "confidence"):
                value = item.get(field)
                if value is not None:
                    normalized_item[field] = value

            if normalized_item:
                normalized_items.append(normalized_item)

    if not normalized_items:
        return None

    return {"items": normalized_items}


def _derive_expected_behavior(
    *,
    runtime_panel: dict[str, Any] | None,
    market_panel: dict[str, Any] | None,
) -> str | None:
    if runtime_panel and runtime_panel.get("event_theme"):
        return str(runtime_panel["event_theme"]).replace("_", " ").strip()

    if market_panel and market_panel.get("event_theme"):
        return str(market_panel["event_theme"]).replace("_", " ").strip()

    return None


def build_closeout_artifact(
    *,
    receipt_payload: dict[str, Any],
    watcher_receipt: dict[str, Any],
    system_view: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    core_id = str(receipt_payload.get("core_id", "market_analyzer_v1")).strip() or "market_analyzer_v1"
    watcher_status = str(
        watcher_receipt.get("watcher_status")
        or watcher_receipt.get("status")
        or ""
    ).strip().lower()

    accepted = watcher_status == "passed"
    closeout_status = "accepted" if accepted else "quarantined"
    requires_review = not accepted

    normalized_system_view = _normalize_system_view(
        system_view=system_view,
        response_payload=response_payload,
    )

    derived_symbol = _derive_symbol(normalized_system_view)
    derived_reference_price = _derive_reference_price(normalized_system_view)
    derived_request_id = _derive_request_id(normalized_system_view)
    derived_generated_at = _derive_generated_at(normalized_system_view)

    case_panel = _copy_case_panel(
        normalized_system_view,
        derived_symbol,
        derived_request_id,
        derived_generated_at,
    )
    runtime_panel = _copy_runtime_panel(normalized_system_view)
    market_panel = _copy_market_panel(
        normalized_system_view,
        derived_symbol,
        derived_reference_price,
    )
    recommendation_panel = _copy_recommendation_panel(normalized_system_view)

    expected_behavior = _derive_expected_behavior(
        runtime_panel=runtime_panel,
        market_panel=market_panel,
    )

    artifact: dict[str, Any] = {
        "closeout_id": _build_closeout_id(core_id),
        "artifact_type": "market_analyzer_closeout",
        "artifact_version": "v2",
        "closed_at": _utc_now_iso(),
        "core_id": core_id,
        "receipt_id": receipt_payload.get("receipt_id"),
        "watcher_validation_id": (
            watcher_receipt.get("validation_id")
            or watcher_receipt.get("watcher_validation_id")
        ),
        "watcher_status": watcher_status,
        "closeout_status": closeout_status,
        "accepted": accepted,
        "requires_review": requires_review,
        "issues": watcher_receipt.get("issues", []),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "policy": {
            "on_pass": "accepted",
            "on_fail": "quarantined",
            "execution_allowed": bool(
                receipt_payload.get("execution_allowed")
                or receipt_payload.get("governance", {}).get("execution_allowed", False)
            ),
            "approval_required": bool(
                receipt_payload.get("approval_required")
                if "approval_required" in receipt_payload
                else receipt_payload.get("governance", {}).get("approval_required", True)
            ),
        },
        "lineage": {
            "source_receipt_id": receipt_payload.get("receipt_id"),
            "source_validation_id": (
                watcher_receipt.get("validation_id")
                or watcher_receipt.get("watcher_validation_id")
            ),
            "source_artifact_type": "market_analyzer_run_receipt",
            "validation_artifact_type": "market_analyzer_receipt_validation",
        },
    }

    if derived_request_id:
        artifact["request_id"] = derived_request_id
    if derived_generated_at:
        artifact["generated_at"] = derived_generated_at
    if derived_symbol:
        artifact["symbol"] = derived_symbol
    if derived_reference_price is not None:
        artifact["reference_price"] = derived_reference_price
    if case_panel:
        artifact["case_panel"] = case_panel
    if runtime_panel:
        artifact["runtime_panel"] = runtime_panel
    if market_panel:
        artifact["market_panel"] = market_panel
    if recommendation_panel:
        artifact["recommendation_panel"] = recommendation_panel
    if expected_behavior:
        artifact["expected_behavior"] = expected_behavior
        artifact["outcome_expectation"] = expected_behavior
        artifact["derived_expected_behavior"] = expected_behavior

    return artifact


def persist_closeout_artifact(closeout_artifact: dict[str, Any]) -> dict[str, Any]:
    closeout_id = str(closeout_artifact.get("closeout_id", "")).strip()
    if not closeout_id:
        raise ValueError("missing_closeout_id")

    closeout_artifact.setdefault("classification", _classification_block())
    closeout_artifact.setdefault("authority", _authority_block())

    path = _closeout_dir() / f"{closeout_id}.json"

    governed_write_json(
        path=path,
        payload=closeout_artifact,
        mutation_class=CLOSEOUT_MUTATION_CLASS,
        persistence_type=CLOSEOUT_PERSISTENCE_TYPE,
        advisory_only=CLOSEOUT_ADVISORY_ONLY,
    )

    return {
        "status": "persisted",
        "closeout_id": closeout_id,
        "path": str(path),
    }


def create_closeout_artifact(
    *,
    receipt_payload: dict[str, Any],
    watcher_receipt: dict[str, Any],
    system_view: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifact = build_closeout_artifact(
        receipt_payload=receipt_payload,
        watcher_receipt=watcher_receipt,
        system_view=system_view,
        response_payload=response_payload,
    )
    persistence = persist_closeout_artifact(artifact)
    artifact["path"] = persistence["path"]
    return artifact


def record_closeout(
    *,
    receipt_payload: dict[str, Any],
    watcher_receipt: dict[str, Any],
    system_view: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return create_closeout_artifact(
        receipt_payload=receipt_payload,
        watcher_receipt=watcher_receipt,
        system_view=system_view,
        response_payload=response_payload,
    )