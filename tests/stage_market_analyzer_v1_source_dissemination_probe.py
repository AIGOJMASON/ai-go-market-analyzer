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
    inbox = inbox_data.get("inbox", {})
    candidates = inbox.get("candidate_cases", [])
    summary = inbox.get("summary", {})

    results = []

    results.append({
        "case": "case_01_inbox_ok",
        "status": "passed" if inbox_response.status_code == 200 else "failed",
    })
    results.append({
        "case": "case_02_signal_count_three",
        "status": "passed" if summary.get("signal_count") == 3 else "failed",
    })
    results.append({
        "case": "case_03_candidate_present",
        "status": "passed" if len(candidates) >= 1 else "failed",
    })

    first_candidate = candidates[0] if candidates else {}
    results.append({
        "case": "case_04_candidate_escalates_to_analyze",
        "status": "passed" if first_candidate.get("suggestion_class") == "analyze" else "failed",
    })
    results.append({
        "case": "case_05_execution_blocked",
        "status": "passed" if inbox_data.get("execution_allowed") is False else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())