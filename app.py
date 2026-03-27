import os

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from AI_GO.api.market_analyzer_api import router as market_analyzer_router
from AI_GO.api.source_signal_desk import router as source_signal_desk_router
from AI_GO.ui.operator_dashboard_ui import router as operator_ui_router
from AI_GO.ui.operator_signal_desk_ui import router as operator_signal_desk_ui_router


def load_allowed_hosts() -> list[str]:
    raw = os.getenv("AI_GO_ALLOWED_HOSTS", "").strip()

    if raw:
        hosts = [host.strip() for host in raw.split(",") if host.strip()]
        if hosts:
            return hosts

    return ["127.0.0.1", "localhost", "testserver"]


app = FastAPI(
    title="AI_GO Market Analyzer V1",
    description="Governed advisory system with unified system_view delivery and source-driven signal desk",
    version="1.1.0",
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=load_allowed_hosts(),
)

app.include_router(market_analyzer_router)
app.include_router(source_signal_desk_router)
app.include_router(operator_ui_router)
app.include_router(operator_signal_desk_ui_router)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "AI_GO Market Analyzer V1",
        "mode": "advisory",
        "routes": {
            "operator": "/operator",
            "operator_signal_desk": "/operator/signal-desk",
            "run": "/market-analyzer/run",
            "run_live": "/market-analyzer/run/live",
            "sources_health": "/market-analyzer/sources/health",
            "sources_ingest": "/market-analyzer/sources/ingest",
            "sources_signals": "/market-analyzer/sources/signals",
            "sources_candidates": "/market-analyzer/sources/candidates",
            "sources_inbox": "/market-analyzer/sources/inbox",
            "sources_analyze_candidate": "/market-analyzer/sources/analyze-candidate",
            "health": "/healthz",
        },
    }


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
