from __future__ import annotations

import importlib

from AI_GO.EXTERNAL_MEMORY.authority.memory_authority_guard import (
    apply_memory_authority_guard,
    evaluate_memory_authority,
)
from AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_registry import RETRIEVAL_REGISTRY


def test_retrieval_registry_imports_and_has_pm_reader() -> None:
    module = importlib.import_module("AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_registry")
    registry = module.RETRIEVAL_REGISTRY

    assert "pm_reader" in registry["allowed_requester_profiles"]
    assert registry["allowed_requester_profiles"]["pm_reader"]["max_records"] == 20
    assert registry["authority"]["memory_is_truth"] is False
    assert registry["authority"]["memory_is_candidate_signal"] is True
    assert registry["authority"]["can_override_state_authority"] is False
    assert registry["authority"]["can_override_canon"] is False
    assert registry["authority"]["can_override_watcher"] is False
    assert registry["authority"]["can_override_execution_gate"] is False


def test_memory_authority_guard_adds_safe_defaults() -> None:
    artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "records": [],
    }

    guarded = apply_memory_authority_guard(artifact)

    assert guarded["sealed"] is True
    assert guarded["authority"]["memory_is_truth"] is False
    assert guarded["authority"]["memory_is_candidate_signal"] is True
    assert guarded["authority"]["advisory_only"] is True
    assert guarded["authority"]["can_execute"] is False
    assert guarded["authority"]["can_mutate_state"] is False
    assert guarded["memory_authority_guard"]["allowed"] is True


def test_memory_authority_guard_blocks_truth_claim() -> None:
    artifact = {
        "artifact_type": "external_memory_promotion_artifact",
        "authority": {
            "memory_is_truth": True,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_state": False,
        },
    }

    decision = evaluate_memory_authority(artifact)

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"
    codes = {error["code"] for error in decision["errors"]}
    assert "memory_authority_claim_must_be_false:memory_is_truth" in codes
    assert "forbidden_memory_authority_claim:memory_is_truth" in codes


def test_memory_authority_guard_blocks_override_claims() -> None:
    artifact = {
        "artifact_type": "external_memory_promotion_artifact",
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": True,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_state": False,
        },
    }

    decision = evaluate_memory_authority(artifact)

    assert decision["allowed"] is False
    codes = {error["code"] for error in decision["errors"]}
    assert "memory_authority_claim_must_be_false:can_override_state_authority" in codes
    assert "forbidden_memory_authority_claim:can_override_state_authority" in codes


def run_probe() -> dict:
    test_retrieval_registry_imports_and_has_pm_reader()
    test_memory_authority_guard_adds_safe_defaults()
    test_memory_authority_guard_blocks_truth_claim()
    test_memory_authority_guard_blocks_override_claims()

    return {
        "status": "passed",
        "phase": "Phase 5F.1",
        "layer": "external_memory_stabilization_and_authority_guard",
        "registry_import_ok": True,
        "pm_reader_restored": True,
        "memory_truth_blocked": True,
        "memory_override_blocked": True,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_state": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5F1_EXTERNAL_MEMORY_GUARD_PROBE: PASS")
    print(result)