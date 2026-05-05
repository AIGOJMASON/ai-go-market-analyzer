from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List


PROBE_VERSION = "stage_full_mutation_surface_scan_v1"

ROOT = Path("AI_GO")

SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
}

LOW_RISK_PATH_PARTS = {
    "tests",
}

DIRECT_MUTATION_PATTERNS = [
    "write_text",
    "write_bytes",
    "json.dump",
    "yaml.dump",
    "pickle.dump",
    "open_write",
    "os.replace",
    "os.remove",
    "unlink",
    "mkdir",
    "rmdir",
    "shutil.copy",
    "shutil.move",
    "append_",
    "write_",
    "persist_",
    "create_",
    "transition_",
    "send_email",
]

GOVERNANCE_MARKERS = [
    "require_governed_mutation",
    "govern_request_from_dict",
    "assert_request_allowed",
    "evaluate_execution_gate",
    "enforce_pre_execution_gate",
    "governed_write_json",
]

REQUIRED_GOVERNED_API_MARKER = "require_governed_mutation"

KNOWN_ALLOWED_LOW_LEVEL_FILES = {
    "AI_GO/core/governance/governed_persistence.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _rel(path: Path) -> str:
    return str(path).replace("\\", "/")


def _is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in path.parts)


def _is_low_risk(path: Path) -> bool:
    return any(part in LOW_RISK_PATH_PARTS for part in path.parts)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _open_is_write(node: ast.Call) -> bool:
    if _call_name(node.func) != "open":
        return False

    args = list(node.args)
    if len(args) >= 2 and isinstance(args[1], ast.Constant):
        mode = str(args[1].value)
        return any(flag in mode for flag in ("w", "a", "x", "+"))

    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode = str(kw.value.value)
            return any(flag in mode for flag in ("w", "a", "x", "+"))

    return False


def _scan_ast(path: Path, text: str) -> List[Dict[str, Any]]:
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

        if _open_is_write(node):
            findings.append(
                {
                    "kind": "direct_mutation",
                    "line": getattr(node, "lineno", 0),
                    "name": "open_write",
                }
            )
            continue

        if name.endswith(".write_text"):
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "write_text"})
        elif name.endswith(".write_bytes"):
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "write_bytes"})
        elif name == "json.dump":
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "json.dump"})
        elif name == "os.replace":
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "os.replace"})
        elif name in {"os.remove", "shutil.copy", "shutil.move"}:
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": name})
        elif name.endswith(".unlink"):
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "unlink"})
        elif name.endswith(".mkdir"):
            findings.append({"kind": "direct_mutation", "line": getattr(node, "lineno", 0), "name": "mkdir"})
        elif name.startswith(("append_", "write_", "persist_", "create_", "transition_")):
            findings.append({"kind": "runtime_mutation_call", "line": getattr(node, "lineno", 0), "name": name})
        elif name == "send_email" or name.endswith(".send_email"):
            findings.append({"kind": "external_mutation_call", "line": getattr(node, "lineno", 0), "name": name})

    return findings


def _has_marker(text: str, marker: str) -> bool:
    return marker in text


def _classify_file(path: Path, text: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    rel = _rel(path)

    has_any_governance = any(_has_marker(text, marker) for marker in GOVERNANCE_MARKERS)
    has_required_guard = _has_marker(text, REQUIRED_GOVERNED_API_MARKER)

    is_api = "/api/" in rel or rel.startswith("AI_GO/api/")
    is_low_level_allowed = rel in KNOWN_ALLOWED_LOW_LEVEL_FILES
    is_test = _is_low_risk(path)

    mutation_count = len(findings)

    unguarded = False
    reason = ""

    if mutation_count == 0:
        reason = "no_mutation_surface_detected"
    elif is_test:
        reason = "test_file_exempt_from_runtime_guard_requirement"
    elif is_low_level_allowed:
        reason = "known_low_level_governed_persistence_file"
    elif is_api and not has_required_guard:
        unguarded = True
        reason = "api_mutation_surface_missing_require_governed_mutation"
    elif not has_any_governance:
        unguarded = True
        reason = "mutation_surface_missing_governance_marker"
    else:
        reason = "mutation_surface_has_governance_marker"

    return {
        "path": rel,
        "mutation_count": mutation_count,
        "unguarded": unguarded,
        "reason": reason,
        "has_require_governed_mutation": has_required_guard,
        "has_any_governance_marker": has_any_governance,
        "findings": findings,
    }


def run_probe() -> Dict[str, Any]:
    files_scanned = 0
    mutation_files: List[Dict[str, Any]] = []
    unguarded_files: List[Dict[str, Any]] = []

    for path in sorted(ROOT.rglob("*.py")):
        if _is_skipped(path):
            continue

        files_scanned += 1
        text = _read(path)
        findings = _scan_ast(path, text)

        if not findings:
            continue

        classified = _classify_file(path, text, findings)
        mutation_files.append(classified)

        if classified["unguarded"]:
            unguarded_files.append(classified)

    status = "passed" if not unguarded_files else "failed"

    output = {
        "status": status,
        "probe_version": PROBE_VERSION,
        "phase": "FULL_MUTATION_SURFACE_SCAN",
        "files_scanned": files_scanned,
        "mutation_file_count": len(mutation_files),
        "unguarded_mutation_file_count": len(unguarded_files),
        "unguarded_mutation_files": unguarded_files,
        "mutation_files": mutation_files,
    }

    print("\n=== FULL MUTATION SURFACE SCAN ===\n")
    print("Files scanned:", files_scanned)
    print("Mutation files:", len(mutation_files))
    print("Unguarded mutation files:", len(unguarded_files))

    if status == "passed":
        print("\n✅ FULL_MUTATION_SURFACE_SCAN: PASS")
    else:
        print("\n❌ FULL_MUTATION_SURFACE_SCAN: FAIL")

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return output


if __name__ == "__main__":
    result = run_probe()
    if result.get("status") != "passed":
        raise SystemExit(1)