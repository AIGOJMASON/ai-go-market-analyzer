MUTATION_CLASSES = {
    "state_write": "Writes to persistent system state",
    "workflow_transition": "Changes workflow phase/state",
    "decision_record": "Logs decision artifacts",
    "risk_record": "Logs risk artifacts",
    "compliance_record": "Logs compliance artifacts",
    "router_update": "Updates routing logic or mappings",
    "oracle_output": "Produces advisory intelligence only",
    "report_generation": "Generates output artifacts (PDF, etc)",
    "intake_record": "Initial project intake creation",
}

PERSISTENCE_TYPES = {
    "filesystem",
    "memory",
    "external",
    "none",
}