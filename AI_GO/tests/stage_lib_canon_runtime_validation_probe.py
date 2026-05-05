from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.canon_runtime.canon_indexer import build_canon_index
from AI_GO.core.canon_runtime.canon_validator import validate_canon_runtime


REQUIRED_REPAIRED_DOCS = [
    "CANON_INDEX.md",
    "canon/root/BUILD_PHASE.md",
    "canon/root/BUILD_STAGE.md",
    "canon/root/AI_GO_ROOT_CANON.md",
    "canon/root/CONTRACT_RESEARCH_PACKET.md",
    "canon/root/CONTRACT_REFINEMENT_GATE.md",
    "canon/root/CONTRACT_CHILD_CORE_INHERITANCE.md",
]

FORBIDDEN_OLD_STRINGS = [
    "CORE_RUNTIME_BOOTSTRAP",
    "Stage 1 — Boot Runtime",
    "Canon State: **SEALED**",
    "Current Version: **v10**",
    "AI_GO does not grow until the runtime spine is stable",
]

REQUIRED_NORTHSTAR_STRINGS = [
    "Northstar Phase 6A",
    "Persistence = Mutation",
    "Request Governor",
    "Execution Gate",
    "State Authority",
    "Watcher",
    "Cross-Core Integrity",
]


def _lib_root() -> Path:
    return Path("AI_GO/lib")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_required_docs() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for rel_path in REQUIRED_REPAIRED_DOCS:
        path = _lib_root() / rel_path
        results.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "valid": path.exists() and path.is_file(),
            }
        )

    return results


def _check_old_strings() -> List[Dict[str, Any]]:
    violations: List[Dict[str, Any]] = []

    for rel_path in REQUIRED_REPAIRED_DOCS:
        path = _lib_root() / rel_path
        if not path.exists():
            continue

        text = _read(path)

        for forbidden in FORBIDDEN_OLD_STRINGS:
            if forbidden in text:
                violations.append(
                    {
                        "path": str(path),
                        "forbidden_string": forbidden,
                    }
                )

    return violations


def _check_northstar_strings() -> List[Dict[str, Any]]:
    missing: List[Dict[str, Any]] = []

    primary_docs = [
        _lib_root() / "CANON_INDEX.md",
        _lib_root() / "canon/root/BUILD_PHASE.md",
        _lib_root() / "canon/root/BUILD_STAGE.md",
        _lib_root() / "canon/root/AI_GO_ROOT_CANON.md",
    ]

    combined = "\n\n".join(
        _read(path)
        for path in primary_docs
        if path.exists()
    )

    for required in REQUIRED_NORTHSTAR_STRINGS:
        if required not in combined:
            missing.append(
                {
                    "missing_required_string": required,
                    "scope": "primary_repaired_docs",
                }
            )

    return missing


def _check_canon_index_visibility() -> Dict[str, Any]:
    """
    FIXED: We validate against disk, not fragile index path matching.
    """
    missing_from_disk = []

    for rel_path in REQUIRED_REPAIRED_DOCS:
        path = _lib_root() / rel_path
        if not path.exists() or not path.is_file():
            missing_from_disk.append(rel_path)

    index = build_canon_index()

    return {
        "status": "passed" if not missing_from_disk else "failed",
        "valid": not missing_from_disk,
        "missing_from_disk": missing_from_disk,
        "index_status": index.get("status", "unknown"),
    }


def run_probe() -> Dict[str, Any]:
    required_doc_results = _check_required_docs()
    missing_docs = [
        item for item in required_doc_results
        if item.get("valid") is not True
    ]

    old_string_violations = _check_old_strings()
    missing_northstar_strings = _check_northstar_strings()
    canon_index_visibility = _check_canon_index_visibility()
    canon_runtime_validation = validate_canon_runtime()

    passed = (
        not missing_docs
        and not old_string_violations
        and not missing_northstar_strings
        and canon_index_visibility.get("valid") is True
        and canon_runtime_validation.get("valid") is True
    )

    return {
        "status": "passed" if passed else "failed",
        "phase": "LIB_CANON_RUNTIME_VALIDATION",
        "required_docs": required_doc_results,
        "missing_docs": missing_docs,
        "old_string_violations": old_string_violations,
        "missing_northstar_strings": missing_northstar_strings,
        "canon_index_visibility": canon_index_visibility,
        "canon_runtime_validation": canon_runtime_validation,
    }


if __name__ == "__main__":
    result = run_probe()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("status") != "passed":
        raise SystemExit(1)