from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json

try:
    from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
except ModuleNotFoundError:
    from historical_market.storage.db_paths import HistoricalMarketPaths


UTC = timezone.utc
CURATED_STORE_VERSION = "northstar_6a_curated_store_v7"

CURATED_DIR_BY_TYPE = {
    "historical_intake_event": "intake_events",
    "historical_merge_event": "merge_events",
    "historical_outcome_event": "outcome_events",
    "historical_setup_pattern": "setup_patterns",
    "historical_asset_relationship": "asset_relationships",
}


@dataclass(frozen=True)
class CuratedWriteResult:
    status: str
    artifact_type: str
    artifact_id: str
    output_path: str
    receipt_path: str
    written_at: str


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_lower(value: Any) -> str:
    return _clean(value).lower()


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _short_hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()[:16]


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
            return parsed.get("payload", default)

        return parsed
    except Exception:
        return default


def _classification(*, persistence_type: str, mutation_class: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "historical_truth_mutation": True,
    }


def _authority_metadata(*, artifact_type: str, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "historical_market_curated_store",
        "operation": operation,
        "artifact_type": artifact_type,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_recommendations": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "governance_stage": "northstar_6a",
        "append_only_memory": True,
    }



class CuratedStore:
    def __init__(self, *, paths: Optional[HistoricalMarketPaths] = None) -> None:
        self.paths = paths or HistoricalMarketPaths()
        self.paths.ensure_all()

    def _curated_root(self) -> Path:
        return self.paths.curated_dir

    def _receipts_root(self) -> Path:
        return self.paths.curated_receipts_dir

    def _dir_for_artifact_type(self, artifact_type: str) -> Path:
        folder = CURATED_DIR_BY_TYPE.get(artifact_type)
        if not folder:
            raise ValueError(f"unsupported curated artifact_type: {artifact_type}")

        candidate = getattr(self.paths, f"{folder}_dir", None)
        if isinstance(candidate, Path):
            return candidate

        return self._curated_root() / folder

    def _artifact_id(self, payload: Mapping[str, Any]) -> str:
        for key in ("artifact_id", "event_id", "pattern_id", "outcome_id", "relationship_id", "record_id"):
            value = _clean(payload.get(key))
            if value:
                return value

        artifact_type = _clean(payload.get("artifact_type")) or "curated"
        return f"{artifact_type}-{_short_hash(payload)}"

    def _artifact_path(self, *, artifact_type: str, artifact_id: str) -> Path:
        return self._dir_for_artifact_type(artifact_type) / f"{artifact_id}.json"

    def _receipt_path(self, *, artifact_type: str, artifact_id: str, written_at: str) -> Path:
        stamp = written_at.replace(":", "").replace("+", "_").replace(".", "_")
        return self._receipts_root() / f"curated-write-{artifact_type}-{artifact_id}-{stamp}.json"

    def write_artifact(
        self,
        artifact: Mapping[str, Any],
        *,
        source: str = "curated_store",
        receipt_id: str = "",
    ) -> CuratedWriteResult:
        if not isinstance(artifact, Mapping):
            raise TypeError("artifact must be a mapping")

        written_at = _utc_now_iso()
        payload = dict(artifact)
        artifact_type = _safe_lower(payload.get("artifact_type"))
        if not artifact_type:
            raise ValueError("artifact_type is required")

        artifact_id = self._artifact_id(payload)

        artifact_mutation_class = "historical_market_curated_persistence"
        artifact_persistence_type = f"{artifact_type}_artifact"
        artifact_authority_metadata = _authority_metadata(
            artifact_type=artifact_type,
            operation="write_curated_artifact",
        )

        payload.setdefault("artifact_id", artifact_id)
        payload.setdefault("written_at", written_at)
        payload["classification"] = _classification(
            persistence_type=artifact_persistence_type,
            mutation_class=artifact_mutation_class,
        )
        payload["authority_metadata"] = artifact_authority_metadata
        payload["execution_allowed"] = False
        payload["sealed"] = True

        artifact_path = self._artifact_path(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
        )

        governed_write_json(
            path=artifact_path,
            payload=payload,
            mutation_class=artifact_mutation_class,
            persistence_type=artifact_persistence_type,
            authority_metadata=artifact_authority_metadata,
        )

        receipt_mutation_class = "historical_market_curated_receipt"
        receipt_persistence_type = "historical_curated_write_receipt"
        receipt_authority_metadata = _authority_metadata(
            artifact_type=artifact_type,
            operation="write_curated_receipt",
        )

        receipt = {
            "artifact_type": "historical_curated_write_receipt",
            "artifact_version": CURATED_STORE_VERSION,
            "receipt_id": _clean(receipt_id) or f"curated-write-{artifact_id}-{written_at}",
            "written_at": written_at,
            "source": _clean(source) or "curated_store",
            "curated_artifact_type": artifact_type,
            "curated_artifact_id": artifact_id,
            "artifact_path": str(artifact_path),
            "classification": _classification(
                persistence_type=receipt_persistence_type,
                mutation_class=receipt_mutation_class,
            ),
            "authority_metadata": receipt_authority_metadata,
            "sealed": True,
        }

        receipt_path = self._receipt_path(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            written_at=written_at,
        )

        governed_write_json(
            path=receipt_path,
            payload=receipt,
            mutation_class=receipt_mutation_class,
            persistence_type=receipt_persistence_type,
            authority_metadata=receipt_authority_metadata,
        )

        return CuratedWriteResult(
            status="written",
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            output_path=str(artifact_path),
            receipt_path=str(receipt_path),
            written_at=written_at,
        )

    def write_curated_artifact(
        self,
        artifact: Mapping[str, Any],
        *,
        source: str = "curated_store",
        receipt_id: str = "",
    ) -> Dict[str, Any]:
        result = self.write_artifact(
            artifact,
            source=source,
            receipt_id=receipt_id,
        )

        return {
            "status": result.status,
            "artifact_type": result.artifact_type,
            "artifact_id": result.artifact_id,
            "output_path": result.output_path,
            "receipt_path": result.receipt_path,
            "written_at": result.written_at,
        }

    def load_artifact(self, *, artifact_type: str, artifact_id: str) -> Dict[str, Any]:
        path = self._artifact_path(
            artifact_type=_safe_lower(artifact_type),
            artifact_id=_clean(artifact_id),
        )
        parsed = _read_json(path, {})
        return parsed if isinstance(parsed, dict) else {}

    def list_artifacts(self, *, artifact_type: str, limit: int = 100) -> list[Dict[str, Any]]:
        root = self._dir_for_artifact_type(_safe_lower(artifact_type))
        rows: list[Dict[str, Any]] = []

        for path in sorted(root.glob("*.json"))[: max(0, int(limit))]:
            parsed = _read_json(path, {})
            if isinstance(parsed, dict):
                rows.append(parsed)

        return rows