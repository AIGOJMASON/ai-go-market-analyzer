from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from AI_GO.core.outcome_feedback.closeout_scan import load_closeout_artifacts
    from AI_GO.core.outcome_feedback.outcome_candidate_builder import (
        build_outcome_candidate_result,
    )
except ImportError:
    from core.outcome_feedback.closeout_scan import load_closeout_artifacts
    from core.outcome_feedback.outcome_candidate_builder import (
        build_outcome_candidate_result,
    )


def _resolve_path_from_argv() -> Path | None:
    if len(sys.argv) < 2:
        return None
    raw = str(sys.argv[1]).strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def _latest_closeout_path() -> Path | None:
    closeouts = load_closeout_artifacts()
    if not closeouts:
        return None

    latest = closeouts[-1]
    raw_path = str(latest.get("path", "")).strip()
    if raw_path:
        path = Path(raw_path)
        if path.exists():
            return path

    closeout_id = str(latest.get("closeout_id", "")).strip()
    if not closeout_id:
        return None

    fallback = (
        Path(__file__).resolve().parents[2]
        / "receipts"
        / "market_analyzer_v1"
        / "closeout"
        / f"{closeout_id}.json"
    )
    if fallback.exists():
        return fallback

    return None


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    explicit_path = _resolve_path_from_argv()

    if explicit_path is not None:
        if not explicit_path.exists():
            print(json.dumps({
                "status": "missing_probe_target",
                "path": str(explicit_path),
            }, indent=2))
            return
        target_path = explicit_path
        source_mode = "explicit_path"
    else:
        target_path = _latest_closeout_path()
        source_mode = "latest_closeout"

        if target_path is None:
            print(json.dumps({
                "status": "missing_latest_closeout",
            }, indent=2))
            return

    payload = _load_payload(target_path)
    result = build_outcome_candidate_result(payload)

    envelope = {
        "probe_source_mode": source_mode,
        "probe_target_path": str(target_path),
        "probe_target_closeout_id": payload.get("closeout_id"),
        "probe_target_request_id": payload.get("request_id") or (payload.get("case_panel") or {}).get("case_id"),
        "result": result,
    }

    print(json.dumps(envelope, indent=2))


if __name__ == "__main__":
    main()