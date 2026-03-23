from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


CORE_ID = "contractor_proposals_core"
DOMAIN_FOCUS = "contractor_proposals"
CORE_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = CORE_ROOT / "outputs"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _output_path(packet_id: str) -> Path:
    return OUTPUTS_DIR / f"{packet_id}__proposal_output.json"


def build_output(execution_record: Dict[str, Any]) -> Dict[str, Any]:
    packet_id = execution_record["packet_id"]
    output = {
        "output_id": f"{packet_id}__proposal_output",
        "core_id": CORE_ID,
        "packet_id": packet_id,
        "domain_focus": DOMAIN_FOCUS,
        "proposal_type": execution_record["proposal_type"],
        "client_request_summary": execution_record["client_request_summary"],
        "recommended_sections": execution_record["recommended_sections"],
        "next_action": execution_record["next_action"],
    }
    output_path = _output_path(packet_id)
    _write_json(output_path, output)
    return {
        "status": "output_built",
        "output_path": output_path.as_posix(),
    }