from __future__ import annotations

from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)
from AI_GO.core.system_brain.external_memory_advisory import (
    build_external_memory_system_brain_advisory,
)
from AI_GO.core.system_brain.system_brain import (
    build_system_brain_context,
    summarize_system_brain_context,
)


def _retrieval_context() -> dict:
    return {
        "artifact_type": "external_memory_read_only_context",
        "status": "ok",
        "retrieval_status": "ok",
        "returned_count": 3,
        "matched_count": 3,
        "retrieval_receipt_id": "extmemread-test",
        "summary": {
            "record_count": 3,
            "symbols_seen": ["XLE"],
            "sectors_seen": ["energy"],
            "trust_classes_seen": ["verified"],
            "pattern_context_available": True,
        },
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
        },
        "sealed": True,
    }


def _promotion_context() -> dict:
    return {
        "artifact_type": "external_memory_promotion_artifact",
        "status": "promoted",
        "promotion_decision": "promoted",
        "promotion_score": 100.0,
        "record_count": 3,
        "reusable_advisory_signal": True,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
        },
        "sealed": True,
    }


def test_external_memory_advisory_panel_is_safe() -> None:
    advisory = build_external_memory_system_brain_advisory(
        retrieval_context=_retrieval_context(),
        promotion_context=_promotion_context(),
    )

    assert advisory["artifact_type"] == "external_memory_system_brain_advisory"
    assert advisory["status"] == "ok"
    assert advisory["pattern_context_available"] is True
    assert advisory["pattern_strength"] == "strong"

    assert advisory["authority"]["memory_is_truth"] is False
    assert advisory["authority"]["memory_is_candidate_signal"] is True
    assert advisory["authority"]["can_execute"] is False
    assert advisory["authority"]["can_mutate_state"] is False
    assert advisory["authority"]["can_mutate_runtime"] is False
    assert advisory["authority"]["can_override_state_authority"] is False
    assert advisory["authority"]["can_override_canon"] is False
    assert advisory["authority"]["can_override_watcher"] is False
    assert advisory["authority"]["can_override_execution_gate"] is False

    assert advisory["use_policy"]["may_feed_system_brain_summary"] is True
    assert advisory["use_policy"]["may_change_recommendations"] is False
    assert advisory["use_policy"]["may_dispatch_actions"] is False


def test_system_brain_accepts_external_memory_as_advisory_only() -> None:
    context = build_system_brain_context(
        external_memory_context=_retrieval_context(),
        external_memory_promotion=_promotion_context(),
    )

    assert context["artifact_type"] == "system_brain_context"
    assert context["mode"] == "read_only"
    assert context["sealed"] is True

    external_memory = context["external_memory"]

    assert external_memory["status"] == "ok"
    assert external_memory["pattern_strength"] == "strong"

    assert context["authority"]["read_only"] is True
    assert context["authority"]["advisory_only"] is True
    assert context["authority"]["can_execute"] is False
    assert context["authority"]["can_mutate_state"] is False
    assert context["authority"]["can_override_governance"] is False
    assert context["authority"]["can_override_watcher"] is False
    assert context["authority"]["can_override_execution_gate"] is False
    assert context["authority"]["can_block_request"] is False
    assert context["authority"]["can_allow_request"] is False

    assert context["use_policy"]["may_change_recommendations"] is False
    assert context["use_policy"]["may_change_pm_strategy"] is False
    assert context["use_policy"]["may_dispatch_actions"] is False


def test_system_brain_summary_exposes_memory_without_authority() -> None:
    context = build_system_brain_context(
        external_memory_context=_retrieval_context(),
        external_memory_promotion=_promotion_context(),
    )
    summary = summarize_system_brain_context(context)

    assert summary["artifact_type"] == "system_brain_summary"
    assert summary["mode"] == "read_only"
    assert summary["external_memory"]["pattern_strength"] == "strong"
    assert summary["external_memory"]["pattern_context_available"] is True
    assert summary["authority"]["can_execute"] is False
    assert summary["authority"]["can_mutate_state"] is False


def test_operator_surface_includes_external_memory_panel() -> None:
    surface = build_operator_system_brain_surface(limit=10)

    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True
    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_mutate_state"] is False
    assert surface["authority"]["can_override_governance"] is False
    assert surface["authority"]["can_override_watcher"] is False
    assert surface["authority"]["can_override_execution_gate"] is False

    assert "external_memory_panel" in surface
    assert surface["external_memory_panel"]["advisory_only"] is True
    assert surface["external_memory_panel"]["authority"].get("can_execute") is False
    assert surface["use_policy"]["may_change_recommendations"] is False
    assert surface["use_policy"]["may_dispatch_actions"] is False


def run_probe() -> dict:
    test_external_memory_advisory_panel_is_safe()
    test_system_brain_accepts_external_memory_as_advisory_only()
    test_system_brain_summary_exposes_memory_without_authority()
    test_operator_surface_includes_external_memory_panel()

    return {
        "status": "passed",
        "phase": "Phase 5F.4",
        "layer": "system_brain_external_memory_advisory_integration",
        "external_memory_visible_to_system_brain": True,
        "operator_surface_panel_present": True,
        "memory_remains_candidate_signal": True,
        "system_brain_remains_read_only": True,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "system_brain_advisory_only": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
            "can_change_recommendations": False,
            "can_change_pm_strategy": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5F4_SYSTEM_BRAIN_EXTERNAL_MEMORY_ADVISORY_PROBE: PASS")
    print(result)