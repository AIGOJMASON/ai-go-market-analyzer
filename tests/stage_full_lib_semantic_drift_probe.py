from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


PROBE_VERSION = "northstar_full_lib_semantic_drift_v1"

LIB_ROOT = Path("AI_GO/lib")

SCAN_SUFFIXES = {".md", ".txt"}

FORBIDDEN_PATTERNS = [
    "CORE_RUNTIME_BOOTSTRAP",
    "AI_GO does not grow until the runtime spine is stable",
    "Canon State: **SEALED**",
    "Current Version: **v10**",
    "child core execution is forbidden",
    "UI interfaces are forbidden",
    "domain automation is forbidden",
    "direct provider access",
    "child core may fetch provider",
    "hidden mutation",
    "hidden persistence",
    "autonomous execution",
    "AI may execute",
    "AI may mutate",
    "System Brain may execute",
    "memory may override",
    "outcome may override",
]

REQUIRED_GLOBAL_CONCEPTS = [
    "Northstar",
    "Persistence = Mutation",
    "Request Governor",
    "Execution Gate",
    "State Authority",
    "Watcher",
    "Cross-Core",
]

AUTHORITY_RISK_PATTERNS = [
    "bypass",
    "override governance",
    "override watcher",
    "override execution gate",
    "direct execution",
    "uncontrolled",
    "autonomous",
    "self-modify",
    "self modify",
]

MUTATION_RISK_PATTERNS = [
    "write",
    "persist",
    "persistence",
    "mutation",
    "mutate",
    "receipt",
    "latest",
    "memory",
    "outcome",
    "dashboard",
    "signoff",
    "closeout",
    "project creation",
]

SAFE_MUTATION_TERMS = [
    "Persistence = Mutation",
    "classified",
    "governed",
    "advisory",
    "non-authoritative",
    "execution_allowed = false",
    "execution_allowed: false",
    "can_execute: false",
    "mutation_allowed: false",
    "Request Governor",
    "Execution Gate",
    "Watcher",
    "State Authority",
    "Cross-Core",
]

SOURCE_RISK_PATTERNS = [
    "source intake",
    "provider",
    "external source",
    "research core",
    "RESEARCH_CORE",
    "child core",
    "child-core",
]

SAFE_SOURCE_TERMS = [
    "RESEARCH_CORE",
    "engine",
    "curation",
    "curated",
    "adapter",
    "raw provider payload",
    "advisory",
    "execution_allowed = false",
    "direct provider access",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _all_docs() -> List[Path]:
    if not LIB_ROOT.exists():
        return []

    docs: List[Path] = []
    for path in LIB_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in SCAN_SUFFIXES:
            docs.append(path)

    return sorted(docs, key=lambda item: str(item).lower())


def _contains_any(text: str, patterns: List[str]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def _matching_patterns(text: str, patterns: List[str]) -> List[str]:
    lowered = text.lower()
    return [
        pattern
        for pattern in patterns
        if pattern.lower() in lowered
    ]


def _scan_forbidden_patterns(path: Path, text: str) -> List[Dict[str, Any]]:
    matches = _matching_patterns(text, FORBIDDEN_PATTERNS)
    return [
        {
            "path": str(path),
            "pattern": pattern,
            "severity": "blocker",
            "reason": "Forbidden legacy or authority-drift language found.",
        }
        for pattern in matches
    ]


def _scan_authority_risk(path: Path, text: str) -> List[Dict[str, Any]]:
    risk_matches = _matching_patterns(text, AUTHORITY_RISK_PATTERNS)
    if not risk_matches:
        return []

    has_safe_terms = _contains_any(text, SAFE_MUTATION_TERMS)

    if has_safe_terms:
        return [
            {
                "path": str(path),
                "patterns": risk_matches,
                "severity": "review",
                "reason": "Authority-risk terms exist but file also contains governance constraint language.",
            }
        ]

    return [
        {
            "path": str(path),
            "patterns": risk_matches,
            "severity": "blocker",
            "reason": "Authority-risk terms found without clear Northstar constraint language.",
        }
    ]


def _scan_mutation_risk(path: Path, text: str) -> List[Dict[str, Any]]:
    risk_matches = _matching_patterns(text, MUTATION_RISK_PATTERNS)
    if not risk_matches:
        return []

    has_safe_terms = _contains_any(text, SAFE_MUTATION_TERMS)

    if has_safe_terms:
        return [
            {
                "path": str(path),
                "patterns": risk_matches,
                "severity": "review",
                "reason": "Mutation-related language exists with constraint language. Review only.",
            }
        ]

    return [
        {
            "path": str(path),
            "patterns": risk_matches,
            "severity": "blocker",
            "reason": "Mutation-related language found without classification or governance language.",
        }
    ]


def _scan_source_flow(path: Path, text: str) -> List[Dict[str, Any]]:
    risk_matches = _matching_patterns(text, SOURCE_RISK_PATTERNS)
    if not risk_matches:
        return []

    has_safe_terms = _contains_any(text, SAFE_SOURCE_TERMS)

    if has_safe_terms:
        return [
            {
                "path": str(path),
                "patterns": risk_matches,
                "severity": "review",
                "reason": "Source-flow language exists with some safe source constraints. Review only.",
            }
        ]

    return [
        {
            "path": str(path),
            "patterns": risk_matches,
            "severity": "blocker",
            "reason": "Source/provider/child-core language found without RESEARCH_CORE, engine, adapter, or advisory constraints.",
        }
    ]


def _scan_global_concepts(docs: List[Path]) -> Dict[str, Any]:
    combined = "\n\n".join(_read_text(path) for path in docs)
    missing = [
        concept
        for concept in REQUIRED_GLOBAL_CONCEPTS
        if concept.lower() not in combined.lower()
    ]

    return {
        "status": "passed" if not missing else "failed",
        "valid": not missing,
        "missing": missing,
    }


def _scan_one(path: Path) -> Dict[str, Any]:
    text = _read_text(path)

    forbidden = _scan_forbidden_patterns(path, text)
    authority_risk = _scan_authority_risk(path, text)
    mutation_risk = _scan_mutation_risk(path, text)
    source_flow_risk = _scan_source_flow(path, text)

    blockers = [
        item
        for item in forbidden + authority_risk + mutation_risk + source_flow_risk
        if item.get("severity") == "blocker"
    ]

    reviews = [
        item
        for item in authority_risk + mutation_risk + source_flow_risk
        if item.get("severity") == "review"
    ]

    return {
        "path": str(path),
        "status": "failed" if blockers else "review" if reviews else "passed",
        "blockers": blockers,
        "reviews": reviews,
    }


def run_probe() -> Dict[str, Any]:
    docs = _all_docs()

    if not docs:
        return {
            "status": "failed",
            "probe_version": PROBE_VERSION,
            "reason": "no_lib_docs_found",
            "lib_root": str(LIB_ROOT),
        }

    per_file = [_scan_one(path) for path in docs]

    failed_files = [
        item for item in per_file
        if item.get("status") == "failed"
    ]

    review_files = [
        item for item in per_file
        if item.get("status") == "review"
    ]

    passed_files = [
        item for item in per_file
        if item.get("status") == "passed"
    ]

    global_concepts = _scan_global_concepts(docs)

    passed = (
        not failed_files
        and global_concepts.get("valid") is True
    )

    return {
        "status": "passed" if passed else "failed",
        "phase": "FULL_LIB_SEMANTIC_DRIFT_SCAN",
        "probe_version": PROBE_VERSION,
        "lib_root": str(LIB_ROOT),
        "doc_count": len(docs),
        "passed_count": len(passed_files),
        "review_count": len(review_files),
        "failed_count": len(failed_files),
        "global_concepts": global_concepts,
        "failed_files": failed_files,
        "review_files": review_files,
    }


if __name__ == "__main__":
    result = run_probe()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("status") != "passed":
        raise SystemExit(1)