from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
from AI_GO.child_cores.market_analyzer_v1.ui.live_test_packet import build_live_test_packet
from AI_GO.child_cores.market_analyzer_v1.ui.ui_payload_builder import build_ui_payload


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def main() -> dict:
    results = []

    try:
        packet = build_live_test_packet()
        runtime_result = run(packet)
        payload = build_ui_payload(runtime_result)

        dashboard = payload.get("dashboard", {})
        views = dashboard.get("views", {})
        ok = (
            payload.get("watcher_passed") is True
            and dashboard.get("artifact_type") == "market_dashboard_output"
            and "recommendations" in views
            and "approval_gate" in views
            and "receipt_trace" in views
        )
        results.append(
            _result(
                "case_01_live_ui_payload",
                "passed" if ok else "failed",
                None if ok else "UI payload missing expected structure",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_live_ui_payload", "failed", str(exc)))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())