from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from AI_GO.child_cores.contractor_builder_v1.api.contractor_builder_api import router as contractor_builder_router
from AI_GO.child_cores.contractor_builder_v1.ui.operator_dashboard_ui import router as operator_ui_router

app = FastAPI(title="AI_GO Contractor Builder V1")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "AI_GO Contractor Builder V1",
        "operator_route": "/operator",
        "health_route": "/healthz",
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "AI_GO Contractor Builder V1",
    }


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

app.include_router(contractor_builder_router)
app.include_router(operator_ui_router)