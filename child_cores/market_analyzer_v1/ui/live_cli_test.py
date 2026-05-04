from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import build_output_views
from AI_GO.child_cores.market_analyzer_v1.ui.cli_renderer import render_dashboard_to_text
from AI_GO.child_cores.market_analyzer_v1.ui.live_test_packet import build_live_test_packet
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result


def main() -> None:
    packet = build_live_test_packet()
    runtime_result = run(packet)
    watcher_result = verify_runtime_result(runtime_result)
    dashboard_output = build_output_views(runtime_result)
    rendered = render_dashboard_to_text(dashboard_output, watcher_result)
    print(rendered)


if __name__ == "__main__":
    main()