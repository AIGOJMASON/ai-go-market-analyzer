from __future__ import annotations

from typing import Any, Dict, List

try:
    from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload  # type: ignore


def _build_payload(
    *,
    request_id: str,
    headline: str,
    observed_at: str,
) -> Dict[str, Any]:
    return {
        "request_id": request_id,
        "case_id": request_id,
        "observed_at": observed_at,
        "macro_context": {
            "headline": headline,
            "macro_bias": "supportive",
        },
        "event_signal": {
            "confirmed": True,
            "event_theme": "energy_rebound",
            "propagation": "moderate",
        },
        "candidates": [
            {
                "symbol": "XLE",
                "sector": "energy",
                "necessity_qualified": True,
                "rebound_confirmed": True,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": "medium",
            }
        ],
    }


def _qualification_record_id(result: Dict[str, Any]) -> str | None:
    runtime_result = result.get("external_memory_runtime_result", {})
    qualification_record = runtime_result.get("qualification_record", {})
    record_id = qualification_record.get("qualification_record_id")
    return record_id if isinstance(record_id, str) else None


def _persisted(result: Dict[str, Any]) -> bool:
    runtime_result = result.get("external_memory_runtime_result", {})
    persistence_receipt = runtime_result.get("persistence_receipt", {})
    return persistence_receipt.get("persistence_decision") == "committed"


def _retrieval_present(result: Dict[str, Any]) -> bool:
    artifact = result.get("external_memory_retrieval_artifact")
    return isinstance(artifact, dict)


def _promotion_present(result: Dict[str, Any]) -> bool:
    artifact = result.get("external_memory_promotion_artifact")
    return isinstance(artifact, dict)


def _memory_panel_present(result: Dict[str, Any]) -> bool:
    panel = result.get("external_memory_panel")
    return isinstance(panel, dict)


def case_01_unique_record_ids_across_similar_events() -> Dict[str, Any]:
    result_1 = run_live_payload(
        _build_payload(
            request_id="probe-retpromo-001",
            headline="Energy disruption expands",
            observed_at="2026-03-29T22:00:00Z",
        )
    )
    result_2 = run_live_payload(
        _build_payload(
            request_id="probe-retpromo-002",
            headline="Energy disruption broadens",
            observed_at="2026-03-29T22:05:00Z",
        )
    )

    id_1 = _qualification_record_id(result_1)
    id_2 = _qualification_record_id(result_2)

    assert isinstance(id_1, str) and id_1
    assert isinstance(id_2, str) and id_2
    assert id_1 != id_2

    return {
        "case": "case_01_unique_record_ids_across_similar_events",
        "status": "passed",
        "details": {
            "record_id_1": id_1,
            "record_id_2": id_2,
        },
    }


def case_02_persistence_commits_for_strong_events() -> Dict[str, Any]:
    result = run_live_payload(
        _build_payload(
            request_id="probe-retpromo-003",
            headline="Energy disruption confirmed",
            observed_at="2026-03-29T22:10:00Z",
        )
    )

    assert _persisted(result) is True

    return {
        "case": "case_02_persistence_commits_for_strong_events",
        "status": "passed",
    }


def case_03_retrieval_path_executes_without_silent_failure() -> Dict[str, Any]:
    # Seed a few related events so retrieval has something to query against.
    seeds: List[Dict[str, Any]] = [
        _build_payload(
            request_id="probe-retpromo-004",
            headline="Energy disruption event one",
            observed_at="2026-03-29T22:15:00Z",
        ),
        _build_payload(
            request_id="probe-retpromo-005",
            headline="Energy disruption event two",
            observed_at="2026-03-29T22:20:00Z",
        ),
        _build_payload(
            request_id="probe-retpromo-006",
            headline="Energy disruption event three",
            observed_at="2026-03-29T22:25:00Z",
        ),
    ]

    last_result: Dict[str, Any] | None = None
    for payload in seeds:
        last_result = run_live_payload(payload)

    assert isinstance(last_result, dict)

    # This probe is intentionally broad:
    # retrieval/promotion should either produce artifacts or at minimum not fail silently.
    runtime_result = last_result.get("external_memory_runtime_result", {})
    assert runtime_result.get("status") == "ok"
    assert last_result.get("external_memory_failed") is not True

    return {
        "case": "case_03_retrieval_path_executes_without_silent_failure",
        "status": "passed",
        "details": {
            "retrieval_present": _retrieval_present(last_result),
            "promotion_present": _promotion_present(last_result),
            "memory_panel_present": _memory_panel_present(last_result),
        },
    }


def run_probe() -> Dict[str, Any]:
    results = [
        case_01_unique_record_ids_across_similar_events(),
        case_02_persistence_commits_for_strong_events(),
        case_03_retrieval_path_executes_without_silent_failure(),
    ]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed
    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())