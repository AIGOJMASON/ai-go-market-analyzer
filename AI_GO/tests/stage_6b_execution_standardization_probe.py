from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set


PHASE = "STAGE_6B_EXECUTION_STANDARDIZATION"
PROBE_VERSION = "stage_6b_execution_standardization_probe_v2_route_scan"

ROOT = Path("AI_GO")
API_ROOT = ROOT / "api"
REPORT_PATH = Path("AI_GO/state/probes/stage_6b_execution_standardization_report.json")

MUTATING_ACTION_MARKERS = [
    "phase_closeout",
    "closeout",
    "signoff",
    "workflow",
    "change",
    "decision",
    "risk",
    "intake",
    "project",
    "report",
    "weekly",
    "promotion",
    "override",
    "refinement",
    "ingress",
    "send_email",
    "delivery",
]

DIRECT_EXECUTION_PATTERNS = [
    ".write_text(",
    ".write_bytes(",
    "json.dump(",
    "open(",
    ".open(",
    "send_email(",
    "write_receipt(",
    "write_pdf_receipt(",
    "write_delivery_receipt(",
    "write_workflow_receipt(",
    "append_client_signoff_status(",
    "build_phase_closeout_pdf(",
]

SAFE_OR_GOVERNED_PATTERNS = [
    "execute_governed_action(",
    "require_governed_mutation(",
    "govern_request_from_dict(",
]

EXCLUDED_API_FILES = {
    "__init__.py",
}


def _norm(path: Path) -> str:
    return str(path).replace("/", "\\")


def _module_name(path: Path) -> str:
    no_suffix = path.with_suffix("")
    return ".".join(no_suffix.parts)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, max(index, 0)) + 1


def _collect_pattern_hits(text: str, patterns: List[str]) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    lines = text.splitlines()

    for pattern in patterns:
        start = 0
        while True:
            index = text.find(pattern, start)
            if index == -1:
                break

            line = _line_number(text, index)
            line_text = lines[line - 1] if 0 <= line - 1 < len(lines) else ""

            hits.append(
                {
                    "pattern": pattern,
                    "line": line,
                    "line_text": line_text.strip()[:220],
                }
            )
            start = index + len(pattern)

    return hits


def _dedupe_hits(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []

    for hit in hits:
        key = f"{hit.get('pattern')}|{hit.get('line')}"
        if key in seen:
            continue
        seen.add(key)
        out.append(hit)

    return out


def _has_api_router(text: str) -> bool:
    return "APIRouter(" in text or "@router." in text


def _has_mutation_intent(path: Path, text: str) -> bool:
    lowered = f"{path.name}\n{text}".lower()
    return any(marker in lowered for marker in MUTATING_ACTION_MARKERS)


def _load_module(path: Path) -> Dict[str, Any]:
    module = _module_name(path)

    try:
        importlib.import_module(module)
        return {
            "status": "ok",
            "module": module,
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "module": module,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _extract_route_functions(path: Path, text: str) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [
            {
                "name": "<syntax_error>",
                "line": getattr(exc, "lineno", 0) or 0,
                "methods": [],
                "path": "",
                "error": str(exc),
            }
        ]

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        route_decorators: List[Dict[str, Any]] = []

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue

            method = func.attr.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue

            base = func.value
            if isinstance(base, ast.Name) and base.id == "router":
                route_path = ""
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    route_path = str(decorator.args[0].value)

                route_decorators.append(
                    {
                        "method": method.upper(),
                        "path": route_path,
                    }
                )

        if route_decorators:
            routes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "routes": route_decorators,
                }
            )

    return routes


def scan_api_file(path: Path) -> Dict[str, Any] | None:
    if path.name in EXCLUDED_API_FILES:
        return None

    text = _read(path)
    if not text:
        return None

    if not _has_api_router(text):
        return None

    module_check = _load_module(path)
    route_functions = _extract_route_functions(path, text)

    direct_hits = _dedupe_hits(_collect_pattern_hits(text, DIRECT_EXECUTION_PATTERNS))
    safe_hits = _dedupe_hits(_collect_pattern_hits(text, SAFE_OR_GOVERNED_PATTERNS))

    mutation_capable = bool(direct_hits)
    uses_execute_governed_action = "execute_governed_action(" in text
    uses_mutation_guard = "require_governed_mutation(" in text
    uses_request_governor = "govern_request_from_dict(" in text or "govern_request(" in text

    requires_6b_conversion = False
    reason = "not_mutation_capable_or_read_only"

    if module_check["status"] != "ok":
        requires_6b_conversion = True
        reason = "module_import_failed"
    elif mutation_capable and uses_execute_governed_action:
        requires_6b_conversion = False
        reason = "uses_execute_governed_action"
    elif mutation_capable and direct_hits and not uses_execute_governed_action:
        requires_6b_conversion = True
        reason = "direct_execution_without_6b_controller"
    elif mutation_capable and uses_request_governor and not uses_execute_governed_action:
        requires_6b_conversion = True
        reason = "governor_check_without_6b_controller"
    elif mutation_capable and uses_mutation_guard:
        requires_6b_conversion = False
        reason = "mutation_guard_only_route"
    elif mutation_capable:
        requires_6b_conversion = True
        reason = "mutation_capable_route_without_6b_controller"
    else:
        requires_6b_conversion = False

    return {
        "path": _norm(path),
        "module": _module_name(path),
        "module_import": module_check,
        "route_functions": route_functions,
        "mutation_capable": mutation_capable,
        "uses_execute_governed_action": uses_execute_governed_action,
        "uses_mutation_guard": uses_mutation_guard,
        "uses_request_governor": uses_request_governor,
        "direct_execution_hits": direct_hits[:50],
        "safe_hits": safe_hits[:50],
        "requires_6b_conversion": requires_6b_conversion,
        "reason": reason,
    }


def run_probe() -> Dict[str, Any]:
    files_scanned = 0
    api_route_files: List[Dict[str, Any]] = []
    mutation_capable_routes: List[Dict[str, Any]] = []
    routes_requiring_conversion: List[Dict[str, Any]] = []

    for path in sorted(API_ROOT.rglob("*.py")):
        files_scanned += 1

        result = scan_api_file(path)
        if result is None:
            continue

        api_route_files.append(result)

        if result["mutation_capable"]:
            mutation_capable_routes.append(result)

        if result["requires_6b_conversion"]:
            routes_requiring_conversion.append(result)

    status = "passed" if not routes_requiring_conversion else "failed"

    output = {
        "status": status,
        "phase": PHASE,
        "probe_version": PROBE_VERSION,
        "files_scanned": files_scanned,
        "api_route_file_count": len(api_route_files),
        "mutation_capable_route_count": len(mutation_capable_routes),
        "routes_requiring_6b_conversion_count": len(routes_requiring_conversion),
        "routes_requiring_6b_conversion": routes_requiring_conversion,
        "report_path": str(REPORT_PATH),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(
            {
                **output,
                "api_route_files": api_route_files,
                "mutation_capable_routes": mutation_capable_routes,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print("\n=== STAGE 6B EXECUTION STANDARDIZATION PROBE ===")
    print("Probe version:", PROBE_VERSION)
    print("API files scanned:", files_scanned)
    print("API route files:", len(api_route_files))
    print("Mutation-capable route files:", len(mutation_capable_routes))
    print("Routes requiring 6B conversion:", len(routes_requiring_conversion))
    print("Report written:", REPORT_PATH)

    if routes_requiring_conversion:
        print("\nRoutes requiring conversion:")
        for item in routes_requiring_conversion:
            print(" -", item["path"], "::", item["reason"])

    if status == "passed":
        print("\n✅ STAGE_6B_EXECUTION_STANDARDIZATION: PASS")
    else:
        print("\n❌ STAGE_6B_EXECUTION_STANDARDIZATION: FAIL")

    return output


if __name__ == "__main__":
    run_probe()