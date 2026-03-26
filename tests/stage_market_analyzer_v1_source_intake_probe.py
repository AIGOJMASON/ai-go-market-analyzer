from fastapi import FastAPI
from fastapi.testclient import TestClient

from AI_GO.api.source_signal_desk import router


def run_probe() -> dict:
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    results = []

    response = client.get("/market-analyzer/sources/health")
    results.append({
        "case": "case_01_health_ok",
        "status": "passed" if response.status_code == 200 and response.json().get("execution_allowed") is False else "failed",
    })

    client.delete("/market-analyzer/sources/reset")

    payload = {
        "request_id": "sig-001",
        "source_item_id": "src-001",
        "source_type": "newswire",
        "headline": "Energy rebound after necessity shock",
        "body": "Refinery disruption appears resolved and energy buying is following through.",
        "symbol_hint": "XLE",
        "sector_hint": "energy",
        "confirmation_hint": "confirmed",
        "price_change_pct": 2.4,
        "source_name": "Newswire A",
        "tags": ["energy", "rebound"],
    }
    response = client.post("/market-analyzer/sources/ingest", json=payload)
    data = response.json()
    signal = data.get("signal", {})

    results.append({
        "case": "case_02_ingest_ok",
        "status": "passed" if response.status_code == 200 and data.get("execution_allowed") is False else "failed",
    })
    results.append({
        "case": "case_03_event_theme_detected",
        "status": "passed" if signal.get("event_theme") == "energy_rebound" else "failed",
    })
    results.append({
        "case": "case_04_symbol_normalized",
        "status": "passed" if signal.get("normalized_symbol") == "XLE" else "failed",
    })

    bad_payload = dict(payload)
    bad_payload["source_item_id"] = "src-bad"
    bad_payload["source_type"] = "unsupported"
    response = client.post("/market-analyzer/sources/ingest", json=bad_payload)
    results.append({
        "case": "case_05_invalid_source_rejected",
        "status": "passed" if response.status_code in {422, 500} else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())