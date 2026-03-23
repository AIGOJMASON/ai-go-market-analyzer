from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.config import AppConfig, validate_startup_config
from api.market_analyzer_api import router as market_analyzer_router


APP_CONFIG: AppConfig | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global APP_CONFIG
    APP_CONFIG = validate_startup_config()
    yield


app = FastAPI(
    title="AI_GO Market Analyzer",
    version="1.0",
    lifespan=lifespan,
)

app.include_router(market_analyzer_router)


@app.middleware("http")
async def add_environment_header(request, call_next):
    response = await call_next(request)
    if APP_CONFIG is not None:
        response.headers["x-ai-go-environment"] = APP_CONFIG.environment
    return response


@app.get("/")
def root() -> dict:
    environment = APP_CONFIG.environment if APP_CONFIG is not None else "unknown"
    return {
        "status": "ok",
        "service": "AI_GO",
        "message": "Market Analyzer API is running",
        "auth_required": True,
        "environment": environment,
    }


@app.get("/healthz")
def healthz() -> dict:
    environment = APP_CONFIG.environment if APP_CONFIG is not None else "unknown"
    return {
        "status": "ok",
        "service": "AI_GO",
        "environment": environment,
    }


if APP_CONFIG is None:
    try:
        _startup_config = validate_startup_config()
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=_startup_config.allowed_hosts,
        )
    except Exception:
        pass
else:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=APP_CONFIG.allowed_hosts,
    )
  
