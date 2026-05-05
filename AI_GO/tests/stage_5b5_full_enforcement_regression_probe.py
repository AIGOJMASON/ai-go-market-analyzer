from __future__ import annotations

import os

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.execution_gate import enforce_pre_execution_gate
from AI_GO.core.governance.cross_core_enforcer import enforce_cross_core_handoff
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


def _headers() -> dict[str, str]:
    api_key = os.getenv("AI_GO_API_KEY", "").strip()
    if not api_key:
        api_key = os.getenv("AI_GO_LOCAL_DEV_API_KEY", "AIGO-local-test").strip()
    return {"x-api-key": api_key}


def _build_engine_handoff() -> dict:
    research_packet = build_live_research_packet(
        {
            "provider": "alpha_vantage",
            "provider_kind": "market_quote",
            "source_type": "verified_api",
            "signal_type": "market_quote",
            "title": "Alpha Vantage quote signal for XLE",
            "summary": "Verified quote provider reports XLE up 1.25%.",
            "symbol": "XLE",
            "price": 91.25,
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
            "provider_payload": {
                "Global Quote": {
                    "01. symbol": "XLE",
                    "05. price": "91.25",
                    "10. change percent": "1.25%",
                }
            },
            "source_material": [
                {
                    "type": "provider_quote",
                    "provider": "alpha_vantage",
                }
            ],
            "source_refs": ["alpha_vantage:GLOBAL_QUOTE"],
            "child_core_targets": ["market_analyzer_v1"],
        }
    )

    return curate_research_packet_for_child_cores(research_packet)


def _assert_watcher_violation(error_payload: dict, expected_layer: str) -> dict:
    detail = error_payload.get("detail", error_payload)
    violation = detail.get("watcher_violation")

    if not isinstance(violation, dict):
        raise AssertionError(
            {
                "error": "missing_watcher_violation",
                "expected_layer": expected_layer,
                "payload": error_payload,
            }
        )

    assert violation.get("artifact_type") == "enforcement_violation_record"
    assert violation.get("layer") == expected_layer
    assert violation.get("policy", {}).get("execution_allowed") is False
    assert violation.get("policy", {}).get("mutation_allowed") is False
    assert violation.get("policy", {}).get("watcher_is_observer_only") is True

    return violation


def _bad_cross_core_packet() -> dict:
    return {
        "source_authority": "root_intelligence_spine",
        "target_child_core": "market_analyzer_v1",
        "spine_order": [
            "engines",
            "child_core_consumption_adapter",
            "child_core",
        ],
        "lineage": {
            "interpretation_packet_id": "engine-demo",
            "adapter_id": "market_analyzer_root_handoff_input",
        },
        "authority": {
            "execution_authority": True,
            "canon_authority": False,
            "governance_override": False,
            "watcher_override": False,
            "state_mutation_authority": False,
            "external_memory_write_authority": False,
            "raw_research_authority": False,
        },
        "external_source": True,
        "raw_input": False,
    }


def _good_cross_core_packet() -> dict:
    return {
        "source_authority": "root_intelligence_spine",
        "target_child_core": "market_analyzer_v1",
        "spine_order": [
            "RESEARCH_CORE",
            "engines",
            "child_core_consumption_adapter",
            "child_core",
        ],
        "lineage": {
            "research_packet_id": "research-demo",
            "interpretation_packet_id": "engine-demo",
            "adapter_id": "market_analyzer_root_handoff_input",
        },
        "authority": {
            "execution_authority": False,
            "canon_authority": False,
            "governance_override": False,
            "watcher_override": False,
            "state_mutation_authority": False,
            "external_memory_write_authority": False,
            "raw_research_authority": False,
        },
        "external_source": True,
        "raw_input": False,
    }


def run_probe() -> dict:
    client = TestClient(app)
    headers = _headers()

    raw_live_response = client.post(
        "/market-analyzer/run/live",
        headers=headers,
        json={
            "request_id": "phase-5b5-raw-live-block",
            "symbol": "XLE",
            "headline": "Raw live payload must be blocked",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
        },
    )

    assert raw_live_response.status_code == 403
    route_violation = _assert_watcher_violation(
        raw_live_response.json(),
        expected_layer="route_enforcement",
    )
    assert route_violation["violation_type"] == "route_violation"
    assert route_violation["severity"] == "low"

    raw_curated_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "request_id": "phase-5b5-raw-curated-block",
            "symbol": "XLE",
            "headline": "Raw payload on curated route must be blocked",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
        },
    )

    assert raw_curated_response.status_code == 400
    raw_curated_violation = _assert_watcher_violation(
        raw_curated_response.json(),
        expected_layer="route_enforcement",
    )
    assert raw_curated_violation["violation_type"] in {
        "missing_curated_packet",
        "raw_payload_rejected",
    }
    assert raw_curated_violation["severity"] == "low"

    engine_handoff = _build_engine_handoff()

    curated_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "request_id": "phase-5b5-curated-live-pass",
            "engine_handoff_packet": engine_handoff,
        },
    )

    if curated_response.status_code != 200:
        raise AssertionError(
            {
                "expected_status": 200,
                "actual_status": curated_response.status_code,
                "response": curated_response.json(),
            }
        )

    curated_payload = curated_response.json()
    assert curated_payload.get("core_id") == "market_analyzer_v1"
    assert curated_payload.get("route_mode") == "pm_route"
    assert curated_payload.get("mode") == "advisory"
    assert curated_payload.get("execution_allowed") is False
    assert curated_payload.get("approval_required") is True

    try:
        enforce_cross_core_handoff(_bad_cross_core_packet())
        raise AssertionError("bad cross-core packet should have been blocked")
    except PermissionError as exc:
        cross_core_error = exc.args[0] if exc.args else {}
        cross_core_violation = cross_core_error.get("watcher_violation", {})

        assert cross_core_error.get("error") == "cross_core_enforcement_blocked"
        assert cross_core_violation.get("layer") == "cross_core_enforcement"
        assert cross_core_violation.get("artifact_type") == "enforcement_violation_record"
        assert cross_core_violation.get("severity") == "high"
        assert cross_core_violation.get("violation_type") in {
            "authority_inflation",
            "invalid_spine_order",
            "cross_core_bypass",
        }

        reason_codes = set(cross_core_violation.get("reason_codes", []))
        assert "forbidden_authority_claim" in reason_codes
        assert "research_core_lineage_missing" in reason_codes

    try:
        enforce_pre_execution_gate(
            {
                "governor_passed": True,
                "canon_passed": True,
                "watcher_passed": False,
                "research_lineage": True,
                "engine_processed": True,
                "adapter_applied": True,
                "external_source": True,
                "raw_input": False,
                "cross_core_packet": _good_cross_core_packet(),
            }
        )
        raise AssertionError("pre-execution gate should have blocked missing watcher")
    except PermissionError as exc:
        pre_gate_error = exc.args[0] if exc.args else {}
        pre_gate_violation = pre_gate_error.get("watcher_violation", {})

        assert pre_gate_error.get("error") == "pre_execution_gate_blocked"
        assert pre_gate_violation.get("layer") == "pre_execution_gate"
        assert pre_gate_violation.get("artifact_type") == "enforcement_violation_record"
        assert pre_gate_violation.get("policy", {}).get("execution_allowed") is False

        pre_gate_reason_codes = set(pre_gate_violation.get("reason_codes", []))
        assert "watcher_required" in pre_gate_reason_codes

    pre_gate_pass = enforce_pre_execution_gate(
        {
            "governor_passed": True,
            "canon_passed": True,
            "watcher_passed": True,
            "research_lineage": True,
            "engine_processed": True,
            "adapter_applied": True,
            "external_source": True,
            "raw_input": False,
            "cross_core_packet": _good_cross_core_packet(),
        }
    )

    assert pre_gate_pass["allowed"] is True

    return {
        "status": "passed",
        "phase": "Phase 5B.5",
        "raw_live_blocked_with_watcher": True,
        "raw_curated_blocked_with_watcher": True,
        "curated_live_allowed": True,
        "cross_core_blocked_with_watcher": True,
        "pre_execution_blocked_with_watcher": True,
        "pre_execution_good_packet_allowed": True,
        "max_severity_watcher_confirmed": True,
        "route_mode": curated_payload.get("route_mode"),
        "execution_allowed": curated_payload.get("execution_allowed"),
        "approval_required": curated_payload.get("approval_required"),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5B5_FULL_ENFORCEMENT_REGRESSION_PROBE: PASS")
    print(result)