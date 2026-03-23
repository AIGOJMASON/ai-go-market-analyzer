from __future__ import annotations

import json

from AI_GO.child_cores.market_analyzer_v1.execution.run import run
from AI_GO.child_cores.market_analyzer_v1.ui.live_test_packet import build_live_test_packet
from AI_GO.child_cores.market_analyzer_v1.ui.ui_payload_builder import build_ui_payload


def main() -> None:
    packet = build_live_test_packet()
    runtime_result = run(packet)
    payload = build_ui_payload(runtime_result)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()