INGRESS_REGISTRY = {
    "layer": "INGRESS_BOUNDARY",
    "identity": "Research + Dispatch ingress separation",

    "subsurfaces": {

        # 🔴 SOURCE INGESTION (PRE-PM)
        "research_live_ingress": {
            "accepted": ["live_market_input"],
            "emitted": ["pm_style_live_input"],
            "description": "Alpha / live quote ingestion boundary",
        },

        "research_event_ingress": {
            "accepted": ["event_input"],
            "emitted": ["pm_style_event_input"],
            "description": "Marketaux event ingestion boundary",
        },

        # 🟢 POST-PM DISPATCH
        "dispatch_ingress_boundary": {
            "accepted": ["dispatch_packet"],
            "emitted": ["ingress_receipt", "ingress_failure_receipt"],
            "description": "PM → child core handoff boundary",
        },
    },
}