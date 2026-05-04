from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import build_output_views
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result


def build_ui_payload(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    dashboard_output = build_output_views(runtime_result)
    watcher_result = verify_runtime_result(runtime_result)

    return {
        "core_id": "market_analyzer_v1",
        "status": "ok",
        "watcher_passed": watcher_result.get("watcher_passed", False),
        "watcher_receipt": watcher_result.get("watcher_receipt"),
        "dashboard": dashboard_output,
    }