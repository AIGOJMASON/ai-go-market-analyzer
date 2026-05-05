from __future__ import annotations

import ast
import os
from typing import Dict, List, Set


PROBE_NAME = "STAGE_DEAD_CODE_PATH_PROBE"

ROOT_PACKAGE = "AI_GO"


def _collect_python_files(root: str) -> List[str]:
    py_files = []
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(".py") and "__pycache__" not in base:
                py_files.append(os.path.join(base, f))
    return py_files


def _module_path_from_file(file_path: str) -> str:
    rel = file_path.replace("\\", "/")
    idx = rel.find(ROOT_PACKAGE)
    if idx == -1:
        return ""

    rel = rel[idx:]
    rel = rel.replace("/", ".")
    rel = rel[:-3]  # strip .py
    return rel


def _extract_imports(file_path: str) -> Set[str]:
    imports = set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

    except Exception:
        pass

    return imports


def run_probe() -> Dict:
    base_path = os.path.abspath(".")
    ai_go_root = os.path.join(base_path, ROOT_PACKAGE)

    files = _collect_python_files(ai_go_root)

    module_map = {}
    all_modules = set()

    for f in files:
        mod = _module_path_from_file(f)
        if mod:
            module_map[f] = mod
            all_modules.add(mod)

    imported_modules = set()

    for f in files:
        imports = _extract_imports(f)
        for imp in imports:
            if imp.startswith(ROOT_PACKAGE):
                imported_modules.add(imp)

    unused_modules = sorted([
        mod for mod in all_modules
        if mod not in imported_modules
        and not mod.endswith("__init__")
    ])

    orphan_files = sorted([
        f for f, mod in module_map.items()
        if mod not in imported_modules
        and not mod.endswith("__init__")
    ])

    return {
        "probe": PROBE_NAME,
        "status": "passed",
        "total_modules": len(all_modules),
        "imported_modules": len(imported_modules),
        "unused_modules_count": len(unused_modules),
        "unused_modules": unused_modules[:50],
        "orphan_files_count": len(orphan_files),
        "orphan_files": orphan_files[:50],
        "mutation_allowed": False,
        "writes_performed": False,
    }


if __name__ == "__main__":
    output = run_probe()
    print(f"{PROBE_NAME}: COMPLETE")
    print("\nOUTPUT:\n", output)