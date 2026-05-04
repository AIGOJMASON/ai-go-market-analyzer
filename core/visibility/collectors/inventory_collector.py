# AI_GO/core/visibility/collectors/inventory_collector.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _child_cores_present() -> List[str]:
    root = PROJECT_ROOT / "child_cores"
    if not root.exists():
        return []

    excluded = {"interfaces", "ingress", "runtime", "output", "review", "watcher"}
    results: List[str] = []

    for entry in root.iterdir():
        if entry.is_dir() and not entry.name.startswith("_") and entry.name not in excluded:
            results.append(entry.name)

    return sorted(results)


def _tests_present(limit: int = 25) -> List[str]:
    root = PROJECT_ROOT / "tests"
    if not root.exists():
        return []
    return sorted([_relative(path) for path in root.rglob("*.py") if path.is_file()])[:limit]


def _handoff_docs_present(limit: int = 25) -> List[str]:
    roots = [
        PROJECT_ROOT / "docs" / "handoffs",
        PROJECT_ROOT / "lib" / "handoffs",
    ]
    results: List[str] = []
    for root in roots:
        if not root.exists():
            continue
        results.extend([_relative(path) for path in root.rglob("*.md") if path.is_file()])
    return sorted(set(results))[:limit]


def _templates_present(limit: int = 25) -> List[str]:
    results: List[str] = []

    explicit_paths = [
        PROJECT_ROOT / "child_cores" / "CHILD_CORE_TEMPLATE_CONTRACT.md",
    ]
    for path in explicit_paths:
        if path.exists():
            results.append(_relative(path))

    for root in [PROJECT_ROOT / "child_cores"]:
        if root.exists():
            results.extend(
                [
                    _relative(path)
                    for path in root.rglob("*TEMPLATE*.md")
                    if path.is_file()
                ]
            )

    return sorted(set(results))[:limit]


def _key_directories() -> List[str]:
    candidates = [
        PROJECT_ROOT / "core",
        PROJECT_ROOT / "state",
        PROJECT_ROOT / "RESEARCH_CORE",
        PROJECT_ROOT / "PM_CORE",
        PROJECT_ROOT / "engines",
        PROJECT_ROOT / "child_cores",
        PROJECT_ROOT / "api",
        PROJECT_ROOT / "tests",
    ]
    return [path.relative_to(PROJECT_ROOT).as_posix() for path in candidates if path.exists()]


def _key_registries(limit: int = 25) -> List[str]:
    results: List[str] = []
    for root in [
        PROJECT_ROOT / "core",
        PROJECT_ROOT / "RESEARCH_CORE",
        PROJECT_ROOT / "PM_CORE",
        PROJECT_ROOT / "child_cores",
    ]:
        if not root.exists():
            continue
        for path in root.rglob("*registry*.py"):
            if path.is_file():
                results.append(_relative(path))
        for path in root.rglob("*REGISTRY*.json"):
            if path.is_file():
                results.append(_relative(path))
    return sorted(set(results))[:limit]


def collect_inventory_view() -> Dict[str, object]:
    child_cores_present = _child_cores_present()
    tests_present = _tests_present()
    handoff_docs_present = _handoff_docs_present()
    templates_present = _templates_present()
    key_directories = _key_directories()
    key_registries = _key_registries()

    return {
        "child_cores_present": child_cores_present,
        "tests_present": tests_present,
        "handoff_docs_present": handoff_docs_present,
        "templates_present": templates_present,
        "key_directories": key_directories,
        "key_registries": key_registries,
        "inventory_counts": {
            "child_cores": len(child_cores_present),
            "tests": len(tests_present),
            "handoffs": len(handoff_docs_present),
            "templates": len(templates_present),
        },
    }