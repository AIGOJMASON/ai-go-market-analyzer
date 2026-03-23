from __future__ import annotations

from pprint import pprint

from AI_GO.core.child_flow.continuity_mutation import (
    process_continuity_mutation,
    reset_store,
)
from AI_GO.core.child_flow.continuity_distribution import (
    DistributionState,
    process_continuity_distribution,
)
from AI_GO.core.child_flow.continuity_distribution.continuity_distribution_registry import (
    CURRENT_DISTRIBUTION_POLICY_VERSION,
)
from AI_GO.core.child_flow.continuity_consumption import (
    ConsumptionState,
    process_continuity_consumption,
)


def _seed_store() -> None:
    reset_store()
    process_continuity_mutation(
        {
            "receipt_type": "continuity_intake_receipt",
            "intake_id": "INTAKE-CONSUME-001",
            "target_core": "louisville_gis_core",
            "continuity_scope": "child_core",
            "admission_basis": "critical_operational_failure",
            "watcher_receipt_ref": "state/receipts/watcher_receipt_consume_001.json",
            "output_disposition_ref": "state/receipts/output_disposition_consume_001.json",
            "runtime_ref": "state/runtime/runtime_receipt_consume_001.json",
            "policy_version": "stage26.v1",
            "timestamp": "2026-03-18T00:00:00Z",
        }
    )
    process_continuity_mutation(
        {
            "receipt_type": "continuity_intake_receipt",
            "intake_id": "INTAKE-CONSUME-002",
            "target_core": "louisville_gis_core",
            "continuity_scope": "child_core",
            "admission_basis": "policy_violation",
            "watcher_receipt_ref": "state/receipts/watcher_receipt_consume_002.json",
            "output_disposition_ref": "state/receipts/output_disposition_consume_002.json",
            "runtime_ref": "state/runtime/runtime_receipt_consume_002.json",
            "policy_version": "stage26.v1",
            "timestamp": "2026-03-19T00:00:00Z",
        }
    )


def _base_distribution_request() -> dict:
    return {
        "request_type": "continuity_read_request",
        "request_id": "DIST-READ-001",
        "requesting_surface": "pm_core",
        "consumer_profile": "pm_core_reader",
        "target_core": "louisville_gis_core",
        "continuity_scope": "child_core",
        "read_reason": "stage29 closeout",
        "requested_view": "latest_n_records",
        "policy_version": CURRENT_DISTRIBUTION_POLICY_VERSION,
        "timestamp": "2026-03-20T00:00:00Z",
    }


def _make_distribution_pair(*, requesting_surface: str, consumer_profile: str, requested_view: str, request_id: str) -> tuple[dict, dict]:
    request = _base_distribution_request()
    request["request_id"] = request_id
    request["requesting_surface"] = requesting_surface
    request["consumer_profile"] = consumer_profile
    request["requested_view"] = requested_view

    result = process_continuity_distribution(request=request, state=DistributionState())
    if result["status"] != "fulfilled":
        raise AssertionError(f"distribution setup failed: {result}")
    return result["artifact"], result["receipt"]


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_probe() -> dict:
    _seed_store()
    results = []

    def record(case_name: str, fn) -> None:
        try:
            fn()
            results.append({"case": case_name, "status": "passed"})
        except Exception as exc:
            results.append({"case": case_name, "status": "failed", "error": str(exc)})

    def case_01_valid_pm_reader_distribution() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-001",
        )
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "fulfilled", f"expected fulfilled, got {result['status']}")
        _assert(result["packet"]["packet_type"] == "continuity_strategy_packet", "wrong packet type")
        _assert(result["receipt"]["receipt_type"] == "continuity_consumption_receipt", "wrong receipt type")
        _assert(result["packet"]["transformation_type"] == "pm_planning_brief", "wrong transformation type")

    def case_02_valid_strategy_reader_distribution() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="strategy_layer",
            consumer_profile="strategy_reader",
            requested_view="summary_stub",
            request_id="DIST-READ-002",
        )
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "fulfilled", f"expected fulfilled, got {result['status']}")
        _assert(result["packet"]["transformation_type"] == "strategy_signal_packet", "wrong transformation type")

    def case_03_valid_child_core_reader_distribution() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="child_core_reader",
            consumer_profile="child_core_reader",
            requested_view="latest_record",
            request_id="DIST-READ-003",
        )
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "fulfilled", f"expected fulfilled, got {result['status']}")
        _assert(result["packet"]["transformation_type"] == "child_core_context_packet", "wrong transformation type")

    def case_04_invalid_artifact_type() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-004",
        )
        artifact["artifact_type"] = "bad_artifact"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "invalid_input", "wrong rejection code")

    def case_05_invalid_receipt_type() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-005",
        )
        receipt["receipt_type"] = "bad_receipt"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "invalid_input", "wrong rejection code")

    def case_06_artifact_receipt_mismatch() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-006",
        )
        receipt["artifact_id"] = "CDA-MISMATCH"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "alignment_invalid", "wrong rejection code")

    def case_07_invalid_consumer_profile() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-007",
        )
        artifact["consumer_profile"] = "unknown_profile"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] in {"alignment_invalid", "consumer_profile_unlawful"}, "wrong rejection code")

    def case_08_invalid_requester_for_profile() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-008",
        )
        receipt["requesting_surface"] = "forbidden_reader"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "requester_unlawful", "wrong rejection code")

    def case_09_invalid_upstream_policy_version() -> None:
        artifact, receipt = _make_distribution_pair(
            requesting_surface="pm_core",
            consumer_profile="pm_core_reader",
            requested_view="latest_n_records",
            request_id="DIST-READ-009",
        )
        receipt["policy_version"] = "stage28.v999"
        result = process_continuity_consumption(
            artifact=artifact,
            receipt=receipt,
            state=ConsumptionState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "policy_version_invalid", "wrong rejection code")

    record("case_01_valid_pm_reader_distribution", case_01_valid_pm_reader_distribution)
    record("case_02_valid_strategy_reader_distribution", case_02_valid_strategy_reader_distribution)
    record("case_03_valid_child_core_reader_distribution", case_03_valid_child_core_reader_distribution)
    record("case_04_invalid_artifact_type", case_04_invalid_artifact_type)
    record("case_05_invalid_receipt_type", case_05_invalid_receipt_type)
    record("case_06_artifact_receipt_mismatch", case_06_artifact_receipt_mismatch)
    record("case_07_invalid_consumer_profile", case_07_invalid_consumer_profile)
    record("case_08_invalid_requester_for_profile", case_08_invalid_requester_for_profile)
    record("case_09_invalid_upstream_policy_version", case_09_invalid_upstream_policy_version)

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "stage": "Stage 29 — Continuity Consumption Boundary",
        "total_cases": len(results),
        "passed": passed,
        "failed": failed,
        "status": "passed" if failed == 0 else "failed",
        "results": results,
    }


if __name__ == "__main__":
    summary = run_probe()
    pprint(summary)
    if summary["failed"] > 0:
        raise SystemExit(1)