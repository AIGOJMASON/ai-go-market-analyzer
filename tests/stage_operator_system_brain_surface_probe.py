from __future__ import annotations

from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)


def run_probe() -> dict:
    surface = build_operator_system_brain_surface()

    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True

    assert surface["authority"]["operator_read_surface"] is True
    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_mutate_state"] is False
    assert surface["authority"]["can_override_governance"] is False
    assert surface["authority"]["can_override_watcher"] is False
    assert surface["authority"]["can_override_execution_gate"] is False
    assert surface["authority"]["can_create_decision"] is False
    assert surface["authority"]["can_escalate_automatically"] is False

    assert surface["use_policy"]["operator_may_read"] is True
    assert surface["use_policy"]["pm_may_read"] is True
    assert surface["use_policy"]["ai_may_read_later"] is True
    assert surface["use_policy"]["may_display_in_dashboard"] is True
    assert surface["use_policy"]["may_change_execution_gate"] is False
    assert surface["use_policy"]["may_change_watcher"] is False
    assert surface["use_policy"]["may_change_state"] is False
    assert surface["use_policy"]["may_write_decisions"] is False
    assert surface["use_policy"]["may_dispatch_actions"] is False

    assert isinstance(surface["plain_summary"], str)
    assert len(surface["plain_summary"]) > 0
    assert isinstance(surface["operator_cards"], list)
    assert len(surface["operator_cards"]) >= 1
    assert isinstance(surface["what_to_watch"], list)

    assert "system_brain" in surface
    assert "unified_awareness_summary" in surface["system_brain"]
    assert "cross_run_summary" in surface["system_brain"]

    return {
        "status": "passed",
        "phase": "Phase 4.9",
        "layer": "operator_system_brain_surface",
        "mode": surface["mode"],
        "card_count": len(surface["operator_cards"]),
        "watch_count": len(surface["what_to_watch"]),
        "plain_summary": surface["plain_summary"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_OPERATOR_SYSTEM_BRAIN_SURFACE_PROBE: PASS")
    print(result)