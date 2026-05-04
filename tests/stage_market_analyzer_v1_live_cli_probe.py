from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
from AI_GO.child_cores.market_analyzer_v1.ui.cli_renderer import render_dashboard_to_text
from AI_GO.child_cores.market_analyzer_v1.ui.live_test_packet import build_live_test_packet
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result
from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import build_output_views


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
        watcher_result = verify_runtime_result(runtime_result)
        dashboard_output = build_output_views(runtime_result)
        rendered = render_dashboard_to_text(dashboard_output, watcher_result)

        ok = (
            "MARKET_ANALYZER_V1 LIVE TEST" in rendered
            and "=== Recommendations ===" in rendered
            and "approval_required=True" in rendered
            and "watcher_passed: True" in rendered
        )
        results.append(
            _result(
                "case_01_live_cli_render",
                "passed" if ok else "failed",
                None if ok else "CLI render missing expected content",
            )
        )
    except Exception as exc:
        results.append(_result("case_01_live_cli_render", "failed", str(exc)))

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())