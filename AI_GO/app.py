# AI_GO/app.py

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles


PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_PARENT = PROJECT_ROOT.parent

for path in (PACKAGE_PARENT, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def get_allowed_hosts() -> list[str]:
    raw = os.getenv("AI_GO_ALLOWED_HOSTS", "*").strip()
    if not raw:
        return ["*"]

    hosts = [part.strip() for part in raw.split(",") if part.strip()]
    return hosts or ["*"]


STATIC_DIR = PROJECT_ROOT / "static"

app = FastAPI(
    title="AI_GO",
    version="1.0.0",
    description="Governed runtime + operator surfaces for AI_GO",
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=get_allowed_hosts())

if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory does not exist: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def include_router_strict(
    module_names: list[str],
    attr_name: str = "router",
) -> dict[str, Any]:
    errors: list[str] = []

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            router = getattr(module, attr_name, None)

            if router is None:
                errors.append(f"{module_name}: missing attribute '{attr_name}'")
                continue

            app.include_router(router)
            print(f"[ROUTER OK] {module_name}")

            return {
                "module": module_name,
                "included": True,
                "reason": None,
            }

        except Exception as exc:
            err = f"{module_name}: {type(exc).__name__}: {exc}"
            print(f"[ROUTER FAIL] {err}")
            errors.append(err)

    raise RuntimeError(
        f"Failed to include router. Tried: {module_names}. Errors: {errors}"
    )


def include_router_optional(
    module_names: list[str],
    attr_name: str = "router",
) -> dict[str, Any]:
    last_error: str | None = None

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            router = getattr(module, attr_name, None)

            if router is not None:
                app.include_router(router)
                print(f"[ROUTER OK OPTIONAL] {module_name}")

                return {
                    "module": module_name,
                    "included": True,
                    "reason": None,
                }

            last_error = f"missing attribute: {attr_name}"

        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"

    print(f"[ROUTER SKIPPED OPTIONAL] {module_names} reason={last_error}")

    return {
        "module": module_names[0],
        "included": False,
        "reason": last_error,
    }


INCLUDED_SURFACES = [
    include_router_strict(
        ["AI_GO.api.market_analyzer_api", "api.market_analyzer_api"]
    ),
    include_router_optional(
        ["AI_GO.api.system_state_api", "api.system_state_api"]
    ),
    include_router_optional(
        ["AI_GO.api.canon_runtime_api", "api.canon_runtime_api"]
    ),
    include_router_optional(
        [
            "AI_GO.api.ai_go_governance_explainer_api",
            "api.ai_go_governance_explainer_api",
        ]
    ),
    include_router_optional(
        ["AI_GO.ui.system_dashboard_ui", "ui.system_dashboard_ui"]
    ),
    include_router_optional(
        ["AI_GO.api.contractor_dashboard_ui", "api.contractor_dashboard_ui"]
    ),
    include_router_optional(
        ["AI_GO.api.contractor_builder_api", "api.contractor_builder_api"]
    ),
]


@app.on_event("startup")
def log_static_state() -> None:
    print("AI_GO startup")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"STATIC_DIR: {STATIC_DIR}")
    print(f"STATIC_DIR exists: {STATIC_DIR.exists()}")

    try:
        files = sorted(p.name for p in STATIC_DIR.iterdir())
    except Exception as exc:
        files = [f"<error reading static dir: {exc}>"]

    print(f"STATIC_DIR files: {files}")
    print(f"INCLUDED_SURFACES: {INCLUDED_SURFACES}")


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "AI_GO",
        "surfaces": {
            "market_analyzer_live_run": "/market-analyzer/run/live",
            "contractor_builder_health": "/contractor-builder/health",
            "contractor_live_dashboard_run": "/contractor-builder/live/dashboard",
            "contractor_dashboard_ui": "/contractor-dashboard",
            "contractor_system_brain_summary": "/contractor-builder/system-brain/summary",
            "contractor_system_brain_surface": "/contractor-builder/system-brain/surface",
            "canon_runtime_health": "/canon-runtime/health",
            "canon_runtime_validate": "/canon-runtime/validate",
            "canon_runtime_index": "/canon-runtime/index",
            "ai_go_explain_governance": "/ai-go/explain-governance",
        },
        "included_surfaces": INCLUDED_SURFACES,
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}