from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


PROBE_VERSION = "northstar_semantic_lock_v1"

LIB_ROOT = Path("AI_GO/lib")

REQUIRED_LOCK_DOCS = [
    LIB_ROOT / "canon" / "root" / "CANONICAL_LANGUAGE_PRIMITIVES.md",
    LIB_ROOT / "canon" / "root" / "NORTHSTAR_SEMANTIC_LOCK_PROFILE.md",
    LIB_ROOT / "canon" / "root" / "REVIEW_COUNT_INTERPRETATION_POLICY.md",
]

REQUIRED_PHRASES = [
    "Persistence = Mutation",
    "RESEARCH_CORE",
    "engine",
    "adapter",
    "execution_allowed = false",
    "State Authority",
    "Watcher",
    "Canon",
    "Request Governor",
    "Execution Gate",
    "Cross-Core Integrity",
]

SEMANTIC_LOCK_PHRASES = [
    "failed_count = 0",
    "global_concepts = passed",
    "review_count",
    "Review_count is not failure",
    "governed complexity",
    "legal grammar of AI_GO",
    "No layer in the system may create authority independently",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def validate_doc(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "valid": False,
            "missing_required_phrases": REQUIRED_PHRASES,
            "missing_lock_phrases": SEMANTIC_LOCK_PHRASES,
        }

    text = read_text(path)

    missing_required = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    missing_lock = [phrase for phrase in SEMANTIC_LOCK_PHRASES if phrase not in text]

    return {
        "path": str(path),
        "exists": True,
        "valid": not missing_required and not missing_lock,
        "missing_required_phrases": missing_required,
        "missing_lock_phrases": missing_lock,
    }


def run_probe() -> Dict[str, Any]:
    doc_results: List[Dict[str, Any]] = [validate_doc(path) for path in REQUIRED_LOCK_DOCS]

    missing_docs = [result for result in doc_results if not result["exists"]]
    invalid_docs = [result for result in doc_results if result["exists"] and not result["valid"]]

    status = "passed" if not missing_docs and not invalid_docs else "failed"

    return {
        "status": status,
        "phase": "NORTHSTAR_SEMANTIC_LOCK",
        "probe_version": PROBE_VERSION,
        "lib_root": str(LIB_ROOT),
        "required_lock_docs": doc_results,
        "missing_docs": missing_docs,
        "invalid_docs": invalid_docs,
        "semantic_lock_state": {
            "failed_count_required": 0,
            "global_concepts_required": "passed",
            "review_count_policy": "review_count_is_not_failure",
            "lock_profile": "active" if status == "passed" else "incomplete",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_probe(), indent=2))