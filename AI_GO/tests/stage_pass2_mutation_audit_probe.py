from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path("AI_GO")

WRITE_PATTERNS = [
    ".write_text(",
    ".write_bytes(",
    "open(",
    "json.dump(",
    "sqlite3.connect(",
    ".execute(",
    "append(",
    "mkdir(",
]

CLASSIFICATION_TERMS = [
    "persistence_type",
    "mutation_class",
    "advisory_only",
]

ALLOWED_MUTATION_CLASSES = {
    "project_creation",
    "visibility_persistence",
    "awareness_persistence",
    "outcome_persistence",
    "outcome_index_persistence",
    "memory_persistence",
    "source_signal_persistence",
    "receipt",
}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _line_number(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx < 0:
        return 0
    return text[:idx].count("\n") + 1


def _is_test_file(path: Path) -> bool:
    return "\\tests\\" in str(path) or "/tests/" in str(path) or path.name.startswith("test_")


def _scan_file(path: Path) -> Dict[str, Any] | None:
    text = _read(path)
    if not text:
        return None

    hits: List[Dict[str, Any]] = []

    for pattern in WRITE_PATTERNS:
        if pattern in text:
            hits.append(
                {
                    "pattern": pattern,
                    "line": _line_number(text, pattern),
                }
            )

    if not hits:
        return None

    has_classification = all(term in text for term in CLASSIFICATION_TERMS)

    mutation_classes_found = sorted(
        set(re.findall(r'"mutation_class"\s*:\s*"([^"]+)"', text))
        | set(re.findall(r"'mutation_class'\s*:\s*'([^']+)'", text))
    )

    invalid_classes = [
        item for item in mutation_classes_found if item not in ALLOWED_MUTATION_CLASSES
    ]

    return {
        "path": str(path),
        "is_test_file": _is_test_file(path),
        "write_hits": hits,
        "has_required_classification_terms": has_classification,
        "mutation_classes_found": mutation_classes_found,
        "invalid_mutation_classes": invalid_classes,
    }


def run_probe() -> Dict[str, Any]:
    scanned_files = 0
    mutation_candidates: List[Dict[str, Any]] = []
    unclassified_runtime_writes: List[Dict[str, Any]] = []
    invalid_mutation_classes: List[Dict[str, Any]] = []

    for path in ROOT.rglob("*.py"):
        scanned_files += 1
        result = _scan_file(path)

        if not result:
            continue

        mutation_candidates.append(result)

        if not result["is_test_file"] and not result["has_required_classification_terms"]:
            unclassified_runtime_writes.append(result)

        if result["invalid_mutation_classes"]:
            invalid_mutation_classes.append(result)

    passed = (
        len(unclassified_runtime_writes) == 0
        and len(invalid_mutation_classes) == 0
    )

    output = {
        "status": "passed" if passed else "failed",
        "phase": "PASS_2_MUTATION_AUDIT",
        "scanned_files": scanned_files,
        "mutation_candidate_count": len(mutation_candidates),
        "unclassified_runtime_write_count": len(unclassified_runtime_writes),
        "invalid_mutation_class_count": len(invalid_mutation_classes),
        "unclassified_runtime_writes": unclassified_runtime_writes,
        "invalid_mutation_classes": invalid_mutation_classes,
        "mutation_candidates": mutation_candidates,
    }

    print("PASS_2_MUTATION_AUDIT:", output["status"].upper())
    print("scanned_files:", scanned_files)
    print("mutation_candidate_count:", len(mutation_candidates))
    print("unclassified_runtime_write_count:", len(unclassified_runtime_writes))
    print("invalid_mutation_class_count:", len(invalid_mutation_classes))

    return output


if __name__ == "__main__":
    print(run_probe())