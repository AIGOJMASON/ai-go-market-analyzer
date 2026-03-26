from fastapi import FastAPI
from fastapi.testclient import TestClient

from AI_GO.api.source_signal_desk import router


def run_probe() -> dict:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    client.delete("/market-analyzer/sources/reset")

    payloads = [
        {
            "request_id": "sig-101",
            "source_item_id": "src-101",
            "source_type": "newswire",
            "headline": "Energy rebound after necessity shock",
            "body": "Refinery disruption appears resolved and energy buying is following through.",
            "symbol_hint": "XLE",
            "sector_hint": "energy",
            "confirmation_hint": "confirmed",
            "price_change_pct": 2.4,
            "source_name": "Newswire A",
            "tags": ["energy", "rebound"],
        },
        {
            "request_id": "sig-102",
            "source_item_id": "src-102",
            "source_type": "rss_feed",
            "headline": "Energy complex extends rebound",
            "body": "Follow-through buying continues after prior necessity shock.",
            "symbol_hint": "XLE",
            "sector_hint": "energy",
            "confirmation_hint": "confirmed",
            "price_change_pct": 2.1,
            "source_name": "Feed B",
            "tags": ["energy"],
        },
        {
            "request_id": "sig-103",
            "source_item_id": "src-103",
            "source_type": "watchlist_note",
            "headline": "Operator notes continued energy strength",
            "body": "Still seeing supportive rebound behavior in energy names.",
            "symbol_hint": "XLE",
            "sector_hint": "energy",
            "confirmation_hint": "partial",
            "price_change_pct": 1.9,
            "source_name": "Desk",
            "tags": ["watchlist"],
        },
    ]

    for payload in payloads:
        client.post("/market-analyzer/sources/ingest", json=payload)

    inbox_response = client.get("/market-analyzer/sources/inbox")
    inbox_data = inbox_response.json()
    candidates = inbox_data.get("inbox", {}).get("candidate_cases", [])
    candidate_id = candidates[0]["candidate_id"] if candidates else None

    bridge_response = client.post(
        "/market-analyzer/sources/analyze-candidate",
        json={
            "candidate_id": candidate_id,
            "request_id": "bridge-test-001",
        },
    )
    bridge_data = bridge_response.json()
    analysis_request = bridge_data.get("analysis_request", {})

    results = []

    results.append({
        "case": "case_01_candidate_present",
        "status": "passed" if candidate_id else "failed",
    })
    results.append({
        "case": "case_02_bridge_ok",
        "status": "passed" if bridge_response.status_code == 200 else "failed",
    })
    results.append({
        "case": "case_03_bridge_request_id_present",
        "status": "passed" if analysis_request.get("request_id") == "bridge-test-001" else "failed",
    })
    results.append({
        "case": "case_04_bridge_symbol_present",
        "status": "passed" if analysis_request.get("symbol") == "XLE" else "failed",
    })
    results.append({
        "case": "case_05_bridge_contract_valid",
        "status": "passed" if set(analysis_request.keys()) == {"request_id", "symbol", "headline", "price_change_pct", "sector", "confirmation"} else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())