from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)


PHASE = "5D.4"
PROBE_ID = "stage_5d4_operator_system_brain_visibility_probe"


FORBIDDEN_AUTHORITY_TRUE = [
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_escalate_automatically",
    "can_block_request",
    "can_allow_request",
]


FORBIDDEN_USE_TRUE = [
    "may_change_canon_decision",
    "may_change_execution_gate",
    "may_change_watcher",
    "may_change_state",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
]


def _assert_surface_shape(surface: dict) -> None:
    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["artifact_version"] == "v1.1"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True

    authority = surface["authority"]
    assert authority["operator_read_surface"] is True
    assert authority["read_only"] is True
    assert authority["advisory_only"] is True

    for key in FORBIDDEN_AUTHORITY_TRUE:
        assert authority.get(key) is False, f"{key} must remain false"

    use_policy = surface["use_policy"]
    assert use_policy["operator_may_read"] is True
    assert use_policy["pm_may_read"] is True
    assert use_policy["may_display_in_dashboard"] is True

    for key in FORBIDDEN_USE_TRUE:
        assert use_policy.get(key) is False, f"{key} must remain false"

    assert isinstance(surface["plain_summary"], str)
    assert surface["plain_summary"]

    assert isinstance(surface["operator_cards"], list)
    assert len(surface["operator_cards"]) >= 1

    assert isinstance(surface["what_to_watch"], list)
    assert len(surface["what_to_watch"]) >= 1

    system_brain = surface["system_brain"]
    assert "system_context_summary" in system_brain
    assert "unified_awareness_summary" in system_brain
    assert "cross_run_summary" in system_brain
    assert "smi_pattern_summary" in system_brain

    source_surfaces = surface["source_surfaces"]
    assert "system_brain_context" in source_surfaces
    assert "unified_system_awareness" in source_surfaces
    assert "cross_run_intelligence" in source_surfaces

    system_context = source_surfaces["system_brain_context"]
    assert system_context["artifact_type"] == "system_brain_context"
    assert system_context["mode"] == "read_only"
    assert system_context["sealed"] is True


def run_probe() -> dict:
    surface = build_operator_system_brain_surface(limit=500)
    _assert_surface_shape(surface)

    client = TestClient(app)

    response = client.get("/contractor-builder/system-brain/surface?limit=500")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    api_surface = payload["surface"]
    _assert_surface_shape(api_surface)

    summary_response = client.get("/contractor-builder/system-brain/summary?limit=500")
    assert summary_response.status_code == 200

    summary_payload = summary_response.json()
    assert summary_payload["status"] == "ok"
    assert summary_payload["mode"] == "read_only"
    assert summary_payload["execution_allowed"] is False
    assert summary_payload["mutation_allowed"] is False

    assert isinstance(summary_payload["plain_summary"], str)
    assert isinstance(summary_payload["operator_cards"], list)
    assert isinstance(summary_payload["what_to_watch"], list)
    assert isinstance(summary_payload["system_brain"], dict)
    assert summary_payload["authority"]["can_execute"] is False
    assert summary_payload["authority"]["can_mutate_state"] is False
    assert summary_payload["use_policy"]["may_change_execution_gate"] is False
    assert summary_payload["use_policy"]["may_write_decisions"] is False

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "surface_version": surface["artifact_version"],
        "operator_cards": len(surface["operator_cards"]),
        "watch_items": len(surface["what_to_watch"]),
        "system_context_visible": "system_context_summary" in surface["system_brain"],
        "api_surface_visible": payload["status"] == "ok",
        "api_summary_visible": summary_payload["status"] == "ok",
        "authority_confirmed": "operator_read_only_advisory_only",
        "next": {
            "phase": "5D.5",
            "recommended_step": "Full System Brain regression across SMI reader, Request Governor, operator surface, and API route.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D4_OPERATOR_SYSTEM_BRAIN_VISIBILITY_PROBE: PASS")
    print(result)