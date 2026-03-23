from __future__ import annotations

CONSUMER_PROFILES = {
    "watcher": {
        "type": "read_only",
        "authority": "none",
        "render_mode": "summary_only",
    },
    "cli": {
        "type": "read_only",
        "authority": "none",
        "render_mode": "summary_with_refs",
    },
    "audit_surface": {
        "type": "read_only",
        "authority": "restricted",
        "render_mode": "closed_artifact",
    },
}