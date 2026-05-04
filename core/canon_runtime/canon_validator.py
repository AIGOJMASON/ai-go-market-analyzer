from __future__ import annotations

from typing import Dict, List

from .canon_indexer import build_canon_index
from .canon_reader import LIB_ROOT, PROJECT_ROOT


REQUIRED_LIB_FILES = (
    "CANON_INDEX.md",
    "DOCUMENT_REGISTRY.json",
    "SYSTEM_READ_ORDER.md",
    "MIGRATION_NOTES.md",
)


REQUIRED_DOMAINS = (
    "core",
    "child_cores",
    "engines",
    "pm_core",
    "research_core",
    "surfaces",
)


def validate_canon_structure() -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []

    if not LIB_ROOT.exists():
        return {
            "status": "failed",
            "valid": False,
            "errors": [f"lib directory does not exist: {LIB_ROOT}"],
            "warnings": [],
        }

    for filename in REQUIRED_LIB_FILES:
        if not (LIB_ROOT / filename).exists():
            errors.append(f"Missing required lib control file: {filename}")

    index = build_canon_index()
    by_domain = index.get("by_domain", {})

    for domain in REQUIRED_DOMAINS:
        if domain not in by_domain:
            errors.append(f"Missing required canon domain: {domain}")

    if not index.get("all_files"):
        errors.append("No canon markdown files found in lib")

    return {
        "status": "passed" if not errors else "failed",
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "lib_root": str(LIB_ROOT),
        "counts": {
            "domain_count": len(by_domain),
            "markdown_file_count": len(index.get("all_files", [])),
            "layer_count": len(index.get("by_layer", {})),
        },
    }


def validate_no_nonlib_layer_docs() -> Dict[str, object]:
    violations: List[str] = []

    for path in PROJECT_ROOT.rglob("*_LAYER.md"):
        normalized = str(path).replace("\\", "/")
        lib_normalized = str(LIB_ROOT).replace("\\", "/")

        if not normalized.startswith(lib_normalized):
            violations.append(str(path))

    return {
        "status": "passed" if not violations else "failed",
        "valid": len(violations) == 0,
        "violations": sorted(violations),
        "violation_count": len(violations),
    }


def validate_canon_runtime() -> Dict[str, object]:
    structure = validate_canon_structure()
    nonlib_docs = validate_no_nonlib_layer_docs()

    valid = bool(structure.get("valid")) and bool(nonlib_docs.get("valid"))

    return {
        "status": "passed" if valid else "failed",
        "valid": valid,
        "structure": structure,
        "nonlib_layer_docs": nonlib_docs,
    }