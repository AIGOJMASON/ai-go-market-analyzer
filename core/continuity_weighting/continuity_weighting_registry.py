
REQUIRED_INPUT_PATHS = [
    "state/smi/current/smi_state.json",
    "state/smi/current/change_ledger.json",
]

OUTPUT_PATH = "state/continuity_weighting/current/continuity_weighting_record.json"

PATTERN_STATUS_RULES = {
    1: {"status": "emerging", "weight": 0.25},
    2: {"status": "strengthening", "weight": 0.50},
    3: {"status": "active", "weight": 0.75},
    4: {"status": "active", "weight": 0.75},
}

DEFAULT_DOMINANT_RULE = {
    "status": "dominant",
    "weight": 1.00,
}

REQUIRED_PATTERN_FIELDS = [
    "continuity_key",
    "recurrence_count",
    "last_seen_timestamp",
    "source_surface",
    "event_class",
    "symbol",
    "event_theme",
    "weight",
    "pattern_status",
]