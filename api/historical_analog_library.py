from copy import deepcopy
from typing import Any, Dict, List

HISTORICAL_ANALOG_LIBRARY: List[Dict[str, Any]] = [
    {
        "analog_id": "analog_supply_expansion_copper_delayed_01",
        "event_theme": "supply_expansion",
        "required_signals": [
            "keyword:chile",
            "keyword:copper",
            "price:positive",
            "confirmation:partial",
            "price_magnitude:medium",
            "legality:lawful_exception",
        ],
        "common_pattern": "Delayed price impact after initial enthusiasm.",
        "failure_mode": "Early reversal before confirmation strengthens.",
        "confidence_band": "medium",
        "pattern_notes": [
            "Supply expansion headlines can trigger a fast first move.",
            "Materials cases often need stronger confirmation before sustained upside appears.",
        ],
    },
    {
        "analog_id": "analog_supply_expansion_materials_fade_02",
        "event_theme": "supply_expansion",
        "required_signals": [
            "sector:materials",
            "price:positive",
            "confirmation:partial",
            "legality:lawful_exception",
        ],
        "common_pattern": "Initial move fades when the market treats supply growth as future dilution of scarcity.",
        "failure_mode": "Headline pop fails when confirmation remains incomplete.",
        "confidence_band": "medium",
        "pattern_notes": [
            "Lawful exception cases can still be structurally fragile.",
            "Partial confirmation often delays durable repricing.",
        ],
    },
    {
        "analog_id": "analog_energy_rebound_confirmed_01",
        "event_theme": "energy_rebound",
        "required_signals": [
            "sector:energy",
            "price:positive",
            "confirmation:confirmed",
            "legality:allowed",
        ],
        "common_pattern": "Follow through is more stable when necessity and confirmation align.",
        "failure_mode": "Breakout fails if price cannot hold support on the next session.",
        "confidence_band": "high",
        "pattern_notes": [
            "Energy rebound cases perform better when the confirmation state is explicit.",
            "Necessity alignment reduces false positives relative to speculative themes.",
        ],
    },
    {
        "analog_id": "analog_geopolitical_energy_spike_01",
        "event_theme": "geopolitical_shock",
        "required_signals": [
            "sector:energy",
            "price:positive",
            "price_magnitude:high",
            "legality:allowed",
        ],
        "common_pattern": "Sharp move can continue briefly, but volatility expands quickly.",
        "failure_mode": "Late entry gets punished when the shock premium compresses.",
        "confidence_band": "medium",
        "pattern_notes": [
            "Shock-driven cases have asymmetric timing risk.",
            "The first move can be correct while still being unsafe to chase.",
        ],
    },
    {
        "analog_id": "analog_speculative_chatter_reject_01",
        "event_theme": "speculative_move",
        "required_signals": [
            "confirmation:none",
            "price:positive",
            "legality:blocked",
        ],
        "common_pattern": "Speculative surge lacks durable support and should not be treated as a lawful recommendation case.",
        "failure_mode": "Momentum collapses once chatter fails to convert into confirmation.",
        "confidence_band": "high",
        "pattern_notes": [
            "Speculative chatter is structurally disallowed.",
            "Observed motion does not equal lawful recommendation authority.",
        ],
    },
    {
        "analog_id": "analog_confirmation_failure_reject_01",
        "event_theme": "confirmation_failure",
        "required_signals": [
            "confirmation:none",
            "legality:blocked",
        ],
        "common_pattern": "Without confirmation, the system should remain defensive and advisory-only.",
        "failure_mode": "Weak evidence gets mistaken for a setup and produces avoidable false positives.",
        "confidence_band": "high",
        "pattern_notes": [
            "Confirmation failure is a control condition, not a signal to improvise.",
            "Low confirmation should compress confidence, not expand it.",
        ],
    },
]


def get_historical_analog_library() -> List[Dict[str, Any]]:
    return deepcopy(HISTORICAL_ANALOG_LIBRARY)