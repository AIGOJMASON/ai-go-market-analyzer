from __future__ import annotations

from typing import Any, Dict, List


APPROVED_SECTORS = {
    "energy",
    "materials",
    "utilities",
    "staples",
    "industrials",
    "unknown",
}

APPROVED_CONFIRMATION = {
    "none",
    "partial",
    "full",
}

APPROVED_EVENT_THEMES = {
    "energy_rebound",
    "supply_expansion",
    "geopolitical_shock",
    "confirmation_failure",
    "speculative_move",
    "unknown",
}

NECESSITY_SECTORS = {
    "energy",
    "utilities",
    "staples",
}

LAWFUL_EVENT_SECTOR_PAIRS = {
    ("supply_expansion", "materials"),
}


class LiveIngressPolicyError(ValueError):
    pass


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def normalize_sector(value: Any) -> str:
    normalized = _clean_text(value).lower()
    if normalized in APPROVED_SECTORS:
        return normalized
    return "unknown"


def normalize_confirmation(value: Any) -> str:
    normalized = _clean_text(value).lower()
    if normalized in APPROVED_CONFIRMATION:
        return normalized
    return "none"


def validate_live_ingress_payload(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise LiveIngressPolicyError("live ingress payload must be a dict")

    request_id = _clean_text(payload.get("request_id"))
    symbol = _clean_text(payload.get("symbol")).upper()
    headline = _clean_text(payload.get("headline"))
    sector = normalize_sector(payload.get("sector"))
    confirmation = normalize_confirmation(payload.get("confirmation"))

    if not request_id:
        raise LiveIngressPolicyError("request_id is required")

    if not symbol:
        raise LiveIngressPolicyError("symbol is required")

    if not headline:
        raise LiveIngressPolicyError("headline is required")

    if sector not in APPROVED_SECTORS:
        raise LiveIngressPolicyError("sector is invalid")

    if confirmation not in APPROVED_CONFIRMATION:
        raise LiveIngressPolicyError("confirmation is invalid")

    price_change_pct = payload.get("price_change_pct")
    if not isinstance(price_change_pct, (int, float)):
        raise LiveIngressPolicyError("price_change_pct must be numeric")


def classify_event_theme(
    *,
    headline: str,
    sector: str,
    confirmation: str,
    price_change_pct: float,
) -> str:
    text = _clean_text(headline).lower()

    if confirmation == "none":
        return "confirmation_failure"

    if "chile" in text or "copper" in text or "mine" in text or "supply" in text:
        return "supply_expansion"

    if "war" in text or "sanction" in text or "missile" in text or "conflict" in text:
        return "geopolitical_shock"

    if sector == "energy" and price_change_pct > 0:
        return "energy_rebound"

    if sector not in NECESSITY_SECTORS:
        return "speculative_move"

    return "unknown"


def derive_macro_bias(event_theme: str, confirmation: str) -> str:
    if event_theme == "energy_rebound" and confirmation in {"partial", "full"}:
        return "supportive"
    if event_theme == "supply_expansion":
        return "mixed"
    if event_theme == "geopolitical_shock":
        return "defensive"
    if event_theme == "confirmation_failure":
        return "cautious"
    if event_theme == "speculative_move":
        return "mixed"
    return "unknown"


def derive_candidate_symbols(symbol: str, sector: str) -> List[str]:
    if sector == "energy":
        return [symbol or "XLE"]
    if sector == "materials":
        return [symbol]
    if sector in {"utilities", "staples", "industrials"}:
        return [symbol]
    return []


def is_lawful_recommendation_context(event_theme: str, sector: str) -> bool:
    if sector in NECESSITY_SECTORS:
        return True
    if (event_theme, sector) in LAWFUL_EVENT_SECTOR_PAIRS:
        return True
    return False


def build_recommendation_seed(
    *,
    symbol: str,
    event_theme: str,
    confirmation: str,
    sector: str,
) -> Dict[str, Any]:
    if not is_lawful_recommendation_context(event_theme, sector):
        return {
            "allowed": False,
            "reason": "no necessity-qualified candidates available",
            "recommendation_count": 0,
            "recommendations": [],
        }

    if confirmation == "none" or event_theme == "confirmation_failure":
        return {
            "allowed": False,
            "reason": "no rebound-validated candidates available",
            "recommendation_count": 0,
            "recommendations": [],
        }

    entry = "wait for confirmation"
    exit_rule = "first failed rebound"
    confidence = "medium"

    if event_theme == "energy_rebound":
        entry = "reclaim support"
        exit_rule = "short-term resistance"
    elif event_theme == "supply_expansion":
        entry = "hold / wait for confirmation"
        exit_rule = "first failed reversal"

    return {
        "allowed": True,
        "reason": None,
        "recommendation_count": 1,
        "recommendations": [
            {
                "symbol": symbol,
                "entry": entry,
                "exit": exit_rule,
                "confidence": confidence,
            }
        ],
    }


def build_refinement_packets(
    *,
    event_theme: str,
    confirmation: str,
    sector: str,
) -> List[Dict[str, Any]]:
    packets: List[Dict[str, Any]] = []
    lawful_context = is_lawful_recommendation_context(event_theme, sector)

    if event_theme == "energy_rebound":
        packets.append(
            {
                "signal": "historical_overreaction_pattern",
                "visible_insight": "Historical necessity rebound cases often reverse if confirmation is weak.",
                "impact": "confidence_reduction",
                "confidence_adjustment": "down",
                "authority": "refinement_influence",
                "source": "live_ingress",
            }
        )

    if event_theme == "supply_expansion":
        packets.append(
            {
                "signal": "delayed_supply_impact_pattern",
                "visible_insight": "Historical supply expansion events often show delayed price impact and early reversals.",
                "impact": "annotation_only",
                "authority": "refinement_influence",
                "source": "live_ingress",
            }
        )

    if confirmation == "none":
        packets.append(
            {
                "signal": "wait_for_confirmation_pattern",
                "visible_insight": "Historical analogs favor confirmation before acting on early rebounds.",
                "impact": "annotation_only",
                "authority": "refinement_influence",
                "source": "live_ingress",
            }
        )

    if not lawful_context:
        packets.append(
            {
                "signal": "speculative_move_filter",
                "visible_insight": "Historical non-necessity moves show weaker follow-through under this policy.",
                "impact": "filter_reinforcement",
                "authority": "refinement_influence",
                "source": "live_ingress",
            }
        )

    return packets


def ensure_lawful_event_theme(event_theme: str) -> str:
    if event_theme not in APPROVED_EVENT_THEMES:
        return "unknown"
    return event_theme