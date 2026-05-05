from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PHASE = "STAGE_6A_MUTATION_SURFACE"
PROBE_VERSION = "stage_6a_mutation_surface_probe_v3_path_anchor"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "state" / "probes" / "stage_6a_mutation_surface_report.json"

EXCLUDED_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "state",
    "receipts",
    "logs",
}

RUNTIME_EXCLUDED_DIR_PARTS = {
    "tests",
    "docs",
    "tools",
    "scripts",
}

CANONICAL_PATH_IMPORTS = {
    "state_root",
    "receipts_root",
    "logs_root",
    "contractor_projects_root",
    "contractor_project_root",
}

CENTRAL_MUTATION_AUTHORITY_FILES = {
    "AI_GO/core/governance/governed_persistence.py",
    "AI_GO/core/receipts/receipt_writer.py",
    "AI_GO/api/receipts.py",
}

PATH_DRIFT_REGEXES = [
    r'Path\(\s*["\']AI_GO[/\\]state',
    r'Path\(\s*["\']state[/\\]',
    r'Path\(\s*["\']state["\']\s*\)',
    r'Path\(\s*["\']AI_GO[/\\]receipts',
    r'Path\(\s*["\']receipts[/\\]',
    r'Path\(\s*["\']receipts["\']\s*\)',
    r'Path\(\s*["\']AI_GO[/\\]logs',
    r'Path\(\s*["\']logs[/\\]',
    r'Path\(\s*["\']logs["\']\s*\)',
    r'["\']AI_GO[/\\]AI_GO[/\\]',
    r'["\']Desktop[/\\]state',
    r'["\']Desktop[/\\]receipts',
    r'["\']Desktop[/\\]logs',
]

DIRECT_WRITE_PATTERNS = [
    ".write_text(",
    ".write_bytes(",
    "json.dump(",
    ".to_json(",
    ".to_csv(",
    ".save(",
    ".dump(",
    "sqlite3.connect(",
    ".execute(",
    ".executemany(",
]

DIRECTORY_MUTATION_PATTERNS = [
    ".mkdir(",
    "mkdir(",
]

EXTERNAL_EFFECT_PATTERNS = [
    "send_email(",
    "send_external(",
    "call_external_service(",
    "requests.post(",
    "requests.put(",
    "requests.patch(",
    "requests.delete(",
]

GOVERNED_TERMS = [
    "governed_write_json",
    "governed_write_raw_json",
    "governed_append_jsonl",
    "governed_persistence",
    "execute_governed_action",
    "require_governed_mutation",
    "authority_metadata",
]

REQUIRED_MUTATION_TERMS = [
    "mutation_class",
    "persistence_type",
    "advisory_only",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _display_path(path: Path) -> str:
    return f"AI_GO/{_rel(path)}"


def _is_under_project_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(PROJECT_ROOT.resolve())
        return True
    except Exception:
        return False


def _is_excluded_path(path: Path) -> bool:
    parts = {part for part in path.parts}
    return bool(parts & EXCLUDED_DIR_PARTS)


def _is_runtime_excluded(path: Path) -> bool:
    rel_parts = set(_rel(path).split("/"))
    return bool(rel_parts & RUNTIME_EXCLUDED_DIR_PARTS)


def _is_test_file(path: Path) -> bool:
    return "tests" in _rel(path).split("/")


def _is_central_mutation_authority(path: Path) -> bool:
    return _display_path(path) in CENTRAL_MUTATION_AUTHORITY_FILES


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _line_at(text: str, line_no: int) -> str:
    lines = text.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def _collect_regex_hits(text: str, regexes: List[str], category: str) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    for pattern in regexes:
        for match in re.finditer(pattern, text):
            line_no = _line_number(text, match.start())
            hits.append(
                {
                    "category": category,
                    "pattern": pattern,
                    "line": line_no,
                    "line_text": _line_at(text, line_no),
                }
            )

    return hits


def _collect_literal_hits(text: str, patterns: List[str], category: str) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    for pattern in patterns:
        start = 0
        while True:
            index = text.find(pattern, start)
            if index == -1:
                break

            line_no = _line_number(text, index)
            hits.append(
                {
                    "category": category,
                    "pattern": pattern,
                    "line": line_no,
                    "line_text": _line_at(text, line_no),
                }
            )
            start = index + len(pattern)

    return hits


def _collect_open_write_hits(path: Path, text: str) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return hits

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        func_name = ""
        if isinstance(func, ast.Name):
            func_name = func.id
        elif isinstance(func, ast.Attribute):
            func_name = func.attr

        if func_name not in {"open"}:
            continue

        mode_value = ""

        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode_value = str(node.args[1].value or "")

        for keyword in node.keywords:
            if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                mode_value = str(keyword.value.value or "")

        if any(flag in mode_value for flag in ("w", "a", "x", "+")):
            line_no = getattr(node, "lineno", 0)
            hits.append(
                {
                    "category": "direct_open_write",
                    "pattern": "open/write-mode",
                    "line": line_no,
                    "line_text": _line_at(text, line_no),
                    "mode": mode_value,
                }
            )

    return hits


def _extract_mutation_classes(text: str) -> List[str]:
    values = set(re.findall(r'["\']mutation_class["\']\s*:\s*["\']([^"\']+)["\']', text))
    values.update(re.findall(r"mutation_class\s*=\s*['\"]([^'\"]+)['\"]", text))
    return sorted(values)


def _has_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def _has_all(text: str, terms: List[str]) -> bool:
    return all(term in text for term in terms)


def _has_canonical_path_import(text: str) -> bool:
    if "AI_GO.core.state_runtime.state_paths" not in text:
        return False
    return any(name in text for name in CANONICAL_PATH_IMPORTS)


def _classify_file(path: Path, text: str) -> Dict[str, Any]:
    path_drift_hits = _collect_regex_hits(text, PATH_DRIFT_REGEXES, "path_drift")
    direct_write_hits = _collect_literal_hits(text, DIRECT_WRITE_PATTERNS, "direct_write")
    directory_hits = _collect_literal_hits(text, DIRECTORY_MUTATION_PATTERNS, "directory_mutation")
    external_hits = _collect_literal_hits(text, EXTERNAL_EFFECT_PATTERNS, "external_effect")
    open_write_hits = _collect_open_write_hits(path, text)

    direct_mutation_hits = direct_write_hits + open_write_hits + external_hits

    is_test = _is_test_file(path)
    runtime_excluded = _is_runtime_excluded(path)
    central_authority = _is_central_mutation_authority(path)

    has_governed_terms = _has_any(text, GOVERNED_TERMS)
    has_required_terms = _has_all(text, REQUIRED_MUTATION_TERMS)
    has_canonical_path_import = _has_canonical_path_import(text)
    mutation_classes = _extract_mutation_classes(text)

    runtime_path_drift_hits = [] if is_test else path_drift_hits

    direct_mutation_bypass = bool(
        direct_mutation_hits
        and not central_authority
        and not has_governed_terms
        and not runtime_excluded
    )

    unclassified_mutation = bool(
        direct_mutation_hits
        and not central_authority
        and not has_required_terms
        and not runtime_excluded
    )

    canonical_path_missing = bool(
        runtime_path_drift_hits
        and not has_canonical_path_import
        and not runtime_excluded
    )

    requires_fix = bool(
        runtime_path_drift_hits
        or direct_mutation_bypass
        or unclassified_mutation
        or canonical_path_missing
    )

    reasons: List[str] = []
    if runtime_path_drift_hits:
        reasons.append("runtime_path_drift")
    if direct_mutation_bypass:
        reasons.append("direct_mutation_bypass")
    if unclassified_mutation:
        reasons.append("unclassified_mutation")
    if canonical_path_missing:
        reasons.append("canonical_path_import_missing")

    if not reasons and path_drift_hits and is_test:
        reasons.append("test_path_drift_warning")
    elif not reasons and directory_hits:
        reasons.append("directory_creation_review")
    elif not reasons:
        reasons.append("clean_or_low_risk")

    return {
        "path": _display_path(path),
        "relative_path": _rel(path),
        "is_test": is_test,
        "runtime_excluded": runtime_excluded,
        "central_mutation_authority": central_authority,
        "requires_fix": requires_fix,
        "reasons": reasons,
        "has_governed_terms": has_governed_terms,
        "has_required_mutation_terms": has_required_terms,
        "has_canonical_path_import": has_canonical_path_import,
        "mutation_classes": mutation_classes,
        "path_drift_hit_count": len(path_drift_hits),
        "runtime_path_drift_hit_count": len(runtime_path_drift_hits),
        "direct_mutation_hit_count": len(direct_mutation_hits),
        "directory_mutation_hit_count": len(directory_hits),
        "path_drift_hits": path_drift_hits[:30],
        "direct_mutation_hits": direct_mutation_hits[:30],
        "directory_mutation_hits": directory_hits[:20],
    }


def scan_file(path: Path) -> Optional[Dict[str, Any]]:
    if _is_excluded_path(path):
        return None

    text = _read(path)
    if not text:
        return None

    result = _classify_file(path, text)

    if (
        result["path_drift_hit_count"] == 0
        and result["direct_mutation_hit_count"] == 0
        and result["directory_mutation_hit_count"] == 0
    ):
        return None

    return result


def run_probe() -> Dict[str, Any]:
    if not PROJECT_ROOT.exists():
        raise RuntimeError(f"project_root_not_found:{PROJECT_ROOT}")

    if PROJECT_ROOT.name != "AI_GO":
        raise RuntimeError(f"project_root_must_be_AI_GO:{PROJECT_ROOT}")

    files_scanned = 0
    flagged_files: List[Dict[str, Any]] = []
    files_requiring_fix: List[Dict[str, Any]] = []
    runtime_path_drift_files: List[Dict[str, Any]] = []
    direct_mutation_bypass_files: List[Dict[str, Any]] = []
    unclassified_mutation_files: List[Dict[str, Any]] = []
    test_path_drift_warnings: List[Dict[str, Any]] = []

    for path in PROJECT_ROOT.rglob("*.py"):
        files_scanned += 1

        result = scan_file(path)
        if result is None:
            continue

        flagged_files.append(result)

        if result["requires_fix"]:
            files_requiring_fix.append(result)

        if result["runtime_path_drift_hit_count"]:
            runtime_path_drift_files.append(result)

        if "direct_mutation_bypass" in result["reasons"]:
            direct_mutation_bypass_files.append(result)

        if "unclassified_mutation" in result["reasons"]:
            unclassified_mutation_files.append(result)

        if "test_path_drift_warning" in result["reasons"]:
            test_path_drift_warnings.append(result)

    passed = len(files_requiring_fix) == 0

    output: Dict[str, Any] = {
        "status": "passed" if passed else "failed",
        "phase": PHASE,
        "probe_version": PROBE_VERSION,
        "generated_at": _utc_now_iso(),
        "project_root": str(PROJECT_ROOT),
        "report_path": str(REPORT_PATH),
        "files_scanned": files_scanned,
        "flagged_file_count": len(flagged_files),
        "files_requiring_fix_count": len(files_requiring_fix),
        "runtime_path_drift_file_count": len(runtime_path_drift_files),
        "direct_mutation_bypass_file_count": len(direct_mutation_bypass_files),
        "unclassified_mutation_file_count": len(unclassified_mutation_files),
        "test_path_drift_warning_count": len(test_path_drift_warnings),
        "files_requiring_fix": files_requiring_fix,
        "runtime_path_drift_files": runtime_path_drift_files,
        "direct_mutation_bypass_files": direct_mutation_bypass_files,
        "unclassified_mutation_files": unclassified_mutation_files,
        "test_path_drift_warnings": test_path_drift_warnings,
        "all_flagged_files": flagged_files,
        "certification": {
            "canonical_project_root_used": _is_under_project_root(REPORT_PATH),
            "relative_root_scan_used": False,
            "cwd_dependent_root_used": False,
            "runtime_path_drift_allowed": False,
            "direct_mutation_bypass_allowed": False,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    print("\n=== STAGE 6A — MUTATION SURFACE + PATH ANCHOR PROBE ===\n")
    print("Probe version:", PROBE_VERSION)
    print("Project root:", PROJECT_ROOT)
    print("Files scanned:", files_scanned)
    print("Flagged files:", len(flagged_files))
    print("Files requiring fix:", len(files_requiring_fix))
    print("Runtime path drift files:", len(runtime_path_drift_files))
    print("Direct mutation bypass files:", len(direct_mutation_bypass_files))
    print("Unclassified mutation files:", len(unclassified_mutation_files))
    print("Test path drift warnings:", len(test_path_drift_warnings))
    print("Report written:", REPORT_PATH)

    if passed:
        print("\n✅ STAGE_6A_MUTATION_SURFACE_PATH_ANCHOR: PASS")
    else:
        print("\n❌ STAGE_6A_MUTATION_SURFACE_PATH_ANCHOR: FAIL")

    return output


if __name__ == "__main__":
    print(run_probe())