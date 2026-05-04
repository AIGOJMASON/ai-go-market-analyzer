# AI_GO/tests/stage_6a_runtime_mutation_surface_probe.py

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path("AI_GO")

PROBE_VERSION = "stage_6a_runtime_mutation_surface_probe_v2"

REQUIRED_TERMS = [
    "mutation_class",
    "persistence_type",
    "authority_metadata",
]

ADVISORY_TERMS = [
    "advisory_only",
    "execution_allowed",
    "runtime_mutation_allowed",
]

EXCLUDED_DIR_PARTS = {
    "tests",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
}

EXCLUDED_FILE_PREFIXES = {
    "test_",
    "stage_",
}

WRITE_METHODS = {
    "write",
    "writelines",
    "write_text",
    "write_bytes",
}

WRITE_OPEN_MODES = {
    "w",
    "a",
    "x",
    "w+",
    "a+",
    "x+",
    "wb",
    "ab",
    "xb",
    "wb+",
    "ab+",
    "xb+",
    "w+b",
    "a+b",
    "x+b",
}

READ_ONLY_OPEN_MODES = {
    "",
    "r",
    "rb",
    "rt",
    "r+",
    "rb+",
    "r+b",
}


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDED_DIR_PARTS:
        return True

    if path.name.startswith(tuple(EXCLUDED_FILE_PREFIXES)):
        return True

    return False


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _node_line(node: ast.AST) -> int:
    return int(getattr(node, "lineno", 0) or 0)


def _constant_string(node: ast.AST | None) -> str:
    if node is None:
        return ""

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.strip()

    if isinstance(node, ast.Str):
        return str(node.s).strip()

    return ""


def _call_name(node: ast.Call) -> str:
    func = node.func

    if isinstance(func, ast.Name):
        return func.id

    if isinstance(func, ast.Attribute):
        return func.attr

    return ""


def _full_call_name(node: ast.Call) -> str:
    func = node.func

    if isinstance(func, ast.Name):
        return func.id

    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value

        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value

        if isinstance(value, ast.Name):
            parts.append(value.id)

        return ".".join(reversed(parts))

    return ""


def _extract_open_mode(node: ast.Call) -> str:
    if len(node.args) >= 2:
        return _constant_string(node.args[1]).lower()

    for keyword in node.keywords:
        if keyword.arg == "mode":
            return _constant_string(keyword.value).lower()

    return "r"


def _is_write_open(node: ast.Call) -> bool:
    name = _call_name(node)
    full_name = _full_call_name(node)

    if name != "open":
        return False

    if full_name.endswith("urlopen"):
        return False

    mode = _extract_open_mode(node)

    if mode in READ_ONLY_OPEN_MODES:
        return False

    if any(flag in mode for flag in ("w", "a", "x")):
        return True

    return mode in WRITE_OPEN_MODES


def _is_write_method(node: ast.Call) -> bool:
    name = _call_name(node)

    if name in {"write_text", "write_bytes"}:
        return True

    if name in {"write", "writelines"}:
        return True

    return False


def _is_json_dump(node: ast.Call) -> bool:
    return _full_call_name(node) == "json.dump"


def _is_sqlite_write_context(node: ast.Call) -> bool:
    full_name = _full_call_name(node)
    return full_name == "sqlite3.connect"


def _is_execute_write_context(node: ast.Call, text: str) -> bool:
    if _call_name(node) != "execute":
        return False

    if not node.args:
        return False

    sql = _constant_string(node.args[0]).lower()
    if not sql:
        return False

    write_sql = (
        "insert ",
        "update ",
        "delete ",
        "create ",
        "drop ",
        "alter ",
        "replace ",
    )

    return sql.lstrip().startswith(write_sql)


def _collect_write_hits(path: Path, text: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _collect_write_hits_fallback(text)

    hits: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if _is_write_open(node):
            hits.append(
                {
                    "pattern": "open_write",
                    "line": _node_line(node),
                    "call": _full_call_name(node),
                    "mode": _extract_open_mode(node),
                }
            )
            continue

        if _is_write_method(node):
            hits.append(
                {
                    "pattern": f".{_call_name(node)}(",
                    "line": _node_line(node),
                    "call": _full_call_name(node),
                }
            )
            continue

        if _is_json_dump(node):
            hits.append(
                {
                    "pattern": "json.dump(",
                    "line": _node_line(node),
                    "call": _full_call_name(node),
                }
            )
            continue

        if _is_sqlite_write_context(node):
            hits.append(
                {
                    "pattern": "sqlite3.connect(",
                    "line": _node_line(node),
                    "call": _full_call_name(node),
                }
            )
            continue

        if _is_execute_write_context(node, text):
            hits.append(
                {
                    "pattern": ".execute(write_sql)",
                    "line": _node_line(node),
                    "call": _full_call_name(node),
                }
            )

    return sorted(hits, key=lambda item: item.get("line", 0))


def _collect_write_hits_fallback(text: str) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []

    fallback_patterns = [
        ".write_text(",
        ".write_bytes(",
        "json.dump(",
        "sqlite3.connect(",
    ]

    for pattern in fallback_patterns:
        for match in re.finditer(re.escape(pattern), text):
            hits.append(
                {
                    "pattern": pattern,
                    "line": text[: match.start()].count("\n") + 1,
                    "call": pattern,
                    "fallback": True,
                }
            )

    for match in re.finditer(r"\bopen\s*\(", text):
        start = match.start()
        window = text[start : start + 160]
        if "urlopen" in text[max(0, start - 12) : start + 12]:
            continue
        if re.search(r"mode\s*=\s*['\"][wax]", window) or re.search(r"['\"][wax]b?\+?['\"]", window):
            hits.append(
                {
                    "pattern": "open_write",
                    "line": text[:start].count("\n") + 1,
                    "call": "open",
                    "fallback": True,
                }
            )

    return sorted(hits, key=lambda item: item.get("line", 0))


def _extract_mutation_classes(text: str) -> List[str]:
    found = set()

    found.update(re.findall(r'"mutation_class"\s*:\s*"([^"]+)"', text))
    found.update(re.findall(r"'mutation_class'\s*:\s*'([^']+)'", text))
    found.update(re.findall(r"mutation_class\s*=\s*['\"]([^'\"]+)['\"]", text))

    return sorted(found)


def _line_window(text: str, line: int, radius: int = 18) -> str:
    lines = text.splitlines()
    if line <= 0:
        return text

    start = max(0, line - radius - 1)
    end = min(len(lines), line + radius)
    return "\n".join(lines[start:end])


def _file_has_required_terms(text: str) -> bool:
    return all(term in text for term in REQUIRED_TERMS)


def _hit_has_required_terms(text: str, hit: Dict[str, Any]) -> bool:
    window = _line_window(text, int(hit.get("line", 0)), radius=24)

    if all(term in window for term in REQUIRED_TERMS):
        return True

    return _file_has_required_terms(text)


def _has_advisory_posture(text: str) -> bool:
    return any(term in text for term in ADVISORY_TERMS)


def scan_file(path: Path) -> Optional[Dict[str, Any]]:
    if _is_excluded(path):
        return None

    text = _read(path)
    if not text:
        return None

    write_hits = _collect_write_hits(path, text)
    if not write_hits:
        return None

    hit_results = []
    for hit in write_hits:
        has_required_terms = _hit_has_required_terms(text, hit)
        hit_results.append(
            {
                **hit,
                "has_required_terms": has_required_terms,
            }
        )

    has_required_terms = all(hit.get("has_required_terms") is True for hit in hit_results)

    return {
        "path": str(path),
        "write_hits": hit_results,
        "has_required_terms": has_required_terms,
        "has_advisory_posture": _has_advisory_posture(text),
        "mutation_classes": _extract_mutation_classes(text),
    }


def run_probe() -> Dict[str, Any]:
    files_scanned = 0
    runtime_mutation_files: List[Dict[str, Any]] = []
    unclassified: List[Dict[str, Any]] = []

    for path in ROOT.rglob("*.py"):
        files_scanned += 1
        result = scan_file(path)

        if result is None:
            continue

        runtime_mutation_files.append(result)

        if not result["has_required_terms"]:
            unclassified.append(result)

    status = "passed" if not unclassified else "failed"

    output = {
        "status": status,
        "phase": "STAGE_6A_RUNTIME_MUTATION_SURFACE",
        "probe_version": PROBE_VERSION,
        "files_scanned": files_scanned,
        "runtime_mutation_file_count": len(runtime_mutation_files),
        "unclassified_runtime_mutation_count": len(unclassified),
        "unclassified_runtime_mutations": unclassified,
        "runtime_mutation_files": runtime_mutation_files,
    }

    print("\n=== STAGE 6A — RUNTIME MUTATION SURFACE PROBE ===\n")
    print("Probe version:", PROBE_VERSION)
    print("Files scanned:", files_scanned)
    print("Runtime mutation files:", len(runtime_mutation_files))
    print("Unclassified runtime mutations:", len(unclassified))

    if status == "passed":
        print("\n✅ STAGE_6A_RUNTIME_MUTATION_SURFACE: PASS")
    else:
        print("\n❌ STAGE_6A_RUNTIME_MUTATION_SURFACE: FAIL")

    print(output)
    return output


if __name__ == "__main__":
    run_probe()