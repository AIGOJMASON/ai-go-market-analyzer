from __future__ import annotations

from typing import Dict, Optional


class ContinuityStore:
    def __init__(self):
        self.records: Dict[str, dict] = {}

    def get(self, continuity_key: str) -> Optional[dict]:
        return self.records.get(continuity_key)

    def exists(self, continuity_key: str) -> bool:
        return continuity_key in self.records

    def write(self, continuity_key: str, record: dict) -> None:
        self.records[continuity_key] = record

    def all(self) -> Dict[str, dict]:
        return self.records

    def reset(self) -> None:
        self.records = {}