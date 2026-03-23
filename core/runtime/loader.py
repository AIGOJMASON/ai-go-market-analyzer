from __future__ import annotations

import importlib.util
import os
from typing import Any, Callable, Dict

from runtime_registry import get_runtime_surface


class RuntimeLoadError(RuntimeError):
    pass


def _repo_root() -> str:
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def _resolve_entrypoint(entrypoint: str) -> tuple[str, str | None]:
    if ":" in entrypoint:
        path_part, attr = entrypoint.split(":", 1)
        return path_part, attr
    return entrypoint, None


def _load_module_from_path(path: str):
    module_name = path.replace("/", "_").replace("\\", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeLoadError(f"Could not load module from path: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_runtime_surface(surface_id: str) -> Any:
    surface = get_runtime_surface(surface_id)
    path_part, attr = _resolve_entrypoint(surface.entrypoint)
    module_path = os.path.join(_repo_root(), path_part)
    if not os.path.exists(module_path):
        raise RuntimeLoadError(f"Entrypoint path not found: {module_path}")
    module = _load_module_from_path(module_path)
    if attr is None:
        return module
    if not hasattr(module, attr):
        raise RuntimeLoadError(f"Entrypoint attribute not found: {attr}")
    return getattr(module, attr)


def load_refinement_arbitrator() -> Callable[..., Dict[str, Any]]:
    loaded = load_runtime_surface("engines.refinement_arbitrator")
    if not callable(loaded):
        raise RuntimeLoadError("Loaded refinement arbitrator entrypoint is not callable.")
    return loaded