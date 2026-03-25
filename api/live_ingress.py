from typing import Any, Dict, List

from AI_GO.api.historical_analog import build_historical_analog_record
from AI_GO.api.live_ingress_schema import LiveIngressPacket, LiveIngressRequest

try:
    from AI_GO.api.event_classifier import build_event_classification  # type: ignore
except ImportError:
    def build_event_classification(payload: Dict[str, Any]) -> Dict[str, Any]:
        headline = str(payload.get("headline", "")).lower()
        sector = str(payload.get("sector", "")).lower()
        confirmation = str(payload.get("confirmation", "")).lower()
        price_change_pct = float(payload.get("price_change_pct", 0.0))

        signals: List[str] = []
        event_theme = "confirmation_failure"
        confidence = "low"

        if "copper" in headline:
            signals.append("keyword:copper")
        if "chile" in headline:
            signals.append("keyword:chile")
        if sector:
            signals.append(f"sector:{sector}")

        if confirmation == "confirmed":
            signals.append("confirmation:confirmed")
        elif confirmation == "partial":
            signals.append("confirmation:partial")
        else:
            signals.append("confirmation:none")

        if price_change_pct > 0:
            signals.append("price:positive")
        elif price_change_pct < 0:
            signals.append("price:negative")
        else:
            signals.append("price:flat")

        if abs(price_change_pct) >= 5:
            signals.append("price_magnitude:high")
        elif abs(price_change_pct) >= 2:
            signals.append("price_magnitude:medium")
        else:
            signals.append("price_magnitude:low")

        if "speculative" in headline or "chatter" in headline:
            event_theme = "speculative_move"
            confidence = "high"
        elif sector == "energy" and price_change_pct > 0 and confirmation in {"confirmed", "partial"}:
            event_theme = "energy_rebound"
            confidence = "high" if confirmation == "confirmed" else "medium"
        elif "iran" in headline or "war" in headline or "attack" in headline:
            event_theme = "geopolitical_shock"
            confidence = "medium"
        elif "mine" in headline or "supply" in headline or "expansion" in headline or "opening" in headline:
            event_theme = "supply_expansion"
            confidence = "medium"
        elif confirmation == "none":
            event_theme = "confirmation_failure"
            confidence = "high"

        return {
            "event_theme": event_theme,
            "classification_confidence": confidence,
            "signals": sorted(set(signals)),
        }

try:
    from AI_GO.api.signal_stack import build_signal_stack_record  # type: ignore
except ImportError:
    def build_signal_stack_record(
        classification_panel: Dict[str, Any],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        stack_signals = set(classification_panel.get("signals", []))
        sector = str(payload.get("sector", "")).lower()
        confirmation = str(payload.get("confirmation", "")).lower()
        price_change_pct = float(payload.get("price_change_pct", 0.0))
        headline = str(payload.get("headline", "")).lower()

        if sector == "energy":
            stack_signals.add("legality:allowed")
        elif sector == "materials" and classification_panel.get("event_theme") == "supply_expansion":
            stack_signals.add("legality:lawful_exception")
        else:
            stack_signals.add("legality:blocked")

        if "speculative" in headline or "chatter" in headline or confirmation == "none":
            stack_signals.discard("legality:allowed")
            stack_signals.discard("legality:lawful_exception")
            stack_signals.add("legality:blocked")

        record = {
            "artifact_type": "signal_stack_record",
            "sealed": True,
            "stack_signals": sorted(stack_signals),
            "stack_summary": {
                "price_direction": (
                    "positive" if price_change_pct > 0 else
                    "negative" if price_change_pct < 0 else
                    "flat"
                ),
                "confirmation_state": confirmation,
                "legality_state": (
                    "allowed" if "legality:allowed" in stack_signals else
                    "lawful_exception" if "legality:lawful_exception" in stack_signals else
                    "blocked"
                ),
                "signal_count": len(stack_signals),
            },
        }
        return record


ALLOWED_CONFIRMATION = {"confirmed", "partial", "none"}


def _validate_request_dict(payload: Dict[str, Any]) -> None:
    required = {
        "request_id",
        "symbol",
        "headline",
        "price_change_pct",
        "sector",
        "confirmation",
    }
    missing = required.difference(payload.keys())
    if missing:
        raise ValueError(f"live ingress payload missing required keys: {sorted(missing)}")

    if str(payload["confirmation"]).lower() not in ALLOWED_CONFIRMATION:
        raise ValueError("confirmation must be one of confirmed, partial, none")


def _build_candidate_panel(payload: Dict[str, Any], signal_stack_record: Dict[str, Any]) -> Dict[str, Any]:
    legality_state = signal_stack_record["stack_summary"]["legality_state"]
    if legality_state in {"allowed", "lawful_exception"}:
        return {
            "candidate_count": 1,
            "symbols": [str(payload["symbol"]).upper()],
        }
    return {
        "candidate_count": 0,
        "symbols": [],
    }


def _build_governance_panel(signal_stack_record: Dict[str, Any]) -> Dict[str, Any]:
    legality_state = signal_stack_record["stack_summary"]["legality_state"]
    confirmation_state = signal_stack_record["stack_summary"]["confirmation_state"]

    watcher_passed = legality_state in {"allowed", "lawful_exception"} and confirmation_state != "none"

    return {
        "watcher_passed": watcher_passed,
        "approval_required": True,
        "execution_allowed": False,
        "advisory_only": True,
    }


def _build_refinement_packet(
    classification_panel: Dict[str, Any],
    signal_stack_record: Dict[str, Any],
    historical_analog_panel: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "refinement_packet",
        "sealed": True,
        "event_theme": classification_panel["event_theme"],
        "signal_count": signal_stack_record["stack_summary"]["signal_count"],
        "analog_confidence_band": historical_analog_panel["confidence_band"],
        "notes": [
            "Refinement input is annotation-only.",
            "Historical analog context must not mutate PM ownership.",
        ],
    }


def build_live_ingress_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    _validate_request_dict(payload)

    normalized_request = LiveIngressRequest(**payload).model_dump()
    classification_panel = build_event_classification(normalized_request)
    signal_stack_panel = build_signal_stack_record(classification_panel, normalized_request)
    historical_analog_panel = build_historical_analog_record(
        classification_panel=classification_panel,
        signal_stack_record=signal_stack_panel,
    )

    market_panel = {
        "market_regime": "normal",
        "event_theme": classification_panel["event_theme"],
        "macro_bias": "mixed",
        "headline": normalized_request["headline"],
        "historical_analog_confidence": historical_analog_panel["confidence_band"],
        "historical_analog_count": historical_analog_panel["analog_count"],
    }

    packet = LiveIngressPacket(
        artifact_type="live_ingress_packet",
        sealed=True,
        request_id=normalized_request["request_id"],
        symbol=str(normalized_request["symbol"]).upper(),
        headline=normalized_request["headline"],
        sector=str(normalized_request["sector"]).lower(),
        confirmation=str(normalized_request["confirmation"]).lower(),
        price_change_pct=float(normalized_request["price_change_pct"]),
        event_theme=classification_panel["event_theme"],
        classification_panel=classification_panel,
        signal_stack_panel=signal_stack_panel,
        historical_analog_panel=historical_analog_panel,
        market_panel=market_panel,
        candidate_panel=_build_candidate_panel(normalized_request, signal_stack_panel),
        governance_panel=_build_governance_panel(signal_stack_panel),
        refinement_packet=_build_refinement_packet(
            classification_panel,
            signal_stack_panel,
            historical_analog_panel,
        ),
        notes=(
            "Bounded live ingress packet with B2 classification, "
            "B3 signal stack, and B4 historical analog context."
        ),
    )

    return packet.model_dump()