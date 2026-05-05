from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List


PROBE_VERSION = "stage_targeted_mutation_bypass_scan_v1"
ROOT = Path("AI_GO")

SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "tests",
}

SAFE_GOVERNANCE_MARKERS = {
    "governed_write_json",
    "governed_write_text",
    "governed_write_bytes",
    "require_governed_mutation",
    "govern_request_from_dict",
    "assert_request_allowed",
    "evaluate_execution_gate",
    "enforce_pre_execution_gate",
}

LOW_LEVEL_ALLOWED_FILES = {
    "AI_GO/core/governance/governed_persistence.py",
}


def _rel(path: Path) -> str:
    return str(path).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _open_write(node: ast.Call) -> bool:
    if _call_name(node.func) != "open":
        return False

    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode = str(node.args[1].value)
        return any(flag in mode for flag in ("w", "a", "x", "+"))

    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
            mode = str(keyword.value.value)
            return any(flag in mode for flag in ("w", "a", "x", "+"))

    return False


def _scan_calls(path: Path, text: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [
            {
                "kind": "syntax_error",
                "line": exc.lineno or 0,
                "name": "syntax_error",
                "detail": str(exc),
            }
        ]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = _call_name(node.func)
        line = getattr(node, "lineno", 0)

        if _open_write(node):
            findings.append({"kind": "direct_write", "line": line, "name": "open_write"})
        elif name == "json.dump":
            findings.append({"kind": "direct_write", "line": line, "name": "json.dump"})
        elif name.endswith(".write_text"):
            findings.append({"kind": "direct_write", "line": line, "name": "write_text"})
        elif name.endswith(".write_bytes"):
            findings.append({"kind": "direct_write", "line": line, "name": "write_bytes"})
        elif name == "os.replace":
            findings.append({"kind": "direct_write", "line": line, "name": "os.replace"})
        elif name in {"os.remove", "shutil.copy", "shutil.move"}:
            findings.append({"kind": "direct_write", "line": line, "name": name})
        elif name.endswith(".unlink"):
            findings.append({"kind": "direct_write", "line": line, "name": "unlink"})
        elif name.endswith(".mkdir"):
            findings.append({"kind": "directory_mutation", "line": line, "name": "mkdir"})

    return findings


def _has_safe_marker(text: str) -> bool:
    return any(marker in text for marker in SAFE_GOVERNANCE_MARKERS)


def _classify(path: Path, text: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    rel = _rel(path)
    has_safe_marker = _has_safe_marker(text)
    is_low_level_allowed = rel in LOW_LEVEL_ALLOWED_FILES
    direct_write_count = sum(1 for item in findings if item["kind"] == "direct_write")
    mkdir_count = sum(1 for item in findings if item["kind"] == "directory_mutation")

    if is_low_level_allowed:
        status = "allowed_low_level_persistence"
        bypass = False
    elif direct_write_count and not has_safe_marker:
        status = "true_bypass_candidate"
        bypass = True
    elif direct_write_count and has_safe_marker:
        status = "review_governed_direct_write"
        bypass = False
    elif mkdir_count and not direct_write_count:
        status = "directory_creation_only_review"
        bypass = False
    else:
        status = "no_bypass_detected"
        bypass = False

    return {
        "path": rel,
        "status": status,
        "bypass": bypass,
        "has_safe_governance_marker": has_safe_marker,
        "direct_write_count": direct_write_count,
        "directory_mutation_count": mkdir_count,
        "findings": findings,
    }


def run_probe() -> Dict[str, Any]:
    files_scanned = 0
    mutation_candidates: List[Dict[str, Any]] = []
    bypass_candidates: List[Dict[str, Any]] = []

    for path in sorted(ROOT.rglob("*.py")):
        if _skip(path):
            continue

        files_scanned += 1
        text = _read(path)
        findings = _scan_calls(path, text)

        if not findings:
            continue

        classified = _classify(path, text, findings)
        mutation_candidates.append(classified)

        if classified["bypass"]:
            bypass_candidates.append(classified)

    result = {
        "status": "passed" if not bypass_candidates else "failed",
        "probe_version": PROBE_VERSION,
        "phase": "TARGETED_MUTATION_BYPASS_SCAN",
        "files_scanned": files_scanned,
        "mutation_candidate_count": len(mutation_candidates),
        "true_bypass_candidate_count": len(bypass_candidates),
        "true_bypass_candidates": bypass_candidates,
        "mutation_candidates": mutation_candidates,
    }

    print("\n=== TARGETED MUTATION BYPASS SCAN ===")
    print("Files scanned:", files_scanned)
    print("Mutation candidates:", len(mutation_candidates))
    print("True bypass candidates:", len(bypass_candidates))

    if result["status"] == "passed":
        print("\n✅ TARGETED_MUTATION_BYPASS_SCAN: PASS")
    else:
        print("\n❌ TARGETED_MUTATION_BYPASS_SCAN: FAIL")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    output = run_probe()
    if output["status"] != "passed":
        raise SystemExit(1)