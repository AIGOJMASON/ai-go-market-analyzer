from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

try:
    from AI_GO.api.market_analyzer_api import router as market_analyzer_router
    from AI_GO.ui.operator_dashboard_ui import router as operator_ui_router
except ModuleNotFoundError:
    from api.market_analyzer_api import router as market_analyzer_router
    from ui.operator_dashboard_ui import router as operator_ui_router


def load_allowed_hosts() -> list[str]:
    """
    Load allowed hosts from environment.

    Env:
      AI_GO_ALLOWED_HOSTS="example.com,api.example.com"

    Safe defaults:
      - localhost
      - 127.0.0.1
      - testserver (for FastAPI TestClient)
    """
    raw = os.getenv("AI_GO_ALLOWED_HOSTS", "").strip()

    if raw:
        hosts = [host.strip() for host in raw.split(",") if host.strip()]
        if hosts:
            return hosts

    return ["127.0.0.1", "localhost", "testserver"]


app = FastAPI(
    title="AI_GO Market Analyzer V1",
    description="Governed advisory system with unified system_view delivery",
    version="1.0.0",
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=load_allowed_hosts(),
)

app.include_router(market_analyzer_router)
app.include_router(operator_ui_router)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "AI_GO Market Analyzer V1",
        "routes": {
            "operator": "/operator",
            "run": "/market-analyzer/run",
            "run_live": "/market-analyzer/run/live",
            "health": "/healthz",
        },
    }


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
