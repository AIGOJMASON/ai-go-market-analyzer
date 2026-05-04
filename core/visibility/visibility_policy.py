# AI_GO/core/visibility/visibility_policy.py

"""
VISIBILITY POLICY

Enforces:
- read-only constraints
- no raw exposure
- bounded shaping
"""

def enforce_no_raw_fields(packet: dict):
    for key in list(packet.keys()):
        if key in ["raw", "files", "logs"]:
            del packet[key]
    return packet


def enforce_required_fields(packet: dict, required_fields: list):
    for field in required_fields:
        if field not in packet:
            packet[field] = {}
    return packet


def enforce_read_only(packet: dict):
    packet["visibility_mode"] = "read_only"
    return packet