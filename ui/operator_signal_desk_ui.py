from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["operator-signal-desk-ui"])


@router.get("/operator/signal-desk", response_class=HTMLResponse)
def operator_signal_desk_page() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Market Signal Desk</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: #0f1115;
      color: #e7eaf0;
    }
    .wrap {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }
    h1, h2, h3 {
      margin-top: 0;
    }
    .subtitle {
      color: #a9b3c4;
      margin-bottom: 24px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .card {
      background: #171b22;
      border: 1px solid #283042;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 16px;
    }
    .full {
      grid-column: 1 / -1;
    }
    label {
      display: block;
      margin-bottom: 6px;
      font-size: 14px;
      color: #cfd7e6;
    }
    input, select, textarea, button {
      width: 100%;
      box-sizing: border-box;
      margin-bottom: 12px;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid #3a4357;
      background: #10141b;
      color: #eef2f8;
    }
    textarea {
      min-height: 100px;
      resize: vertical;
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    .actions button {
      width: auto;
      min-width: 160px;
      cursor: pointer;
    }
    .pill {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid #4a5877;
      margin-right: 8px;
      margin-bottom: 8px;
      font-size: 12px;
    }
    .list-item {
      border-top: 1px solid #283042;
      padding-top: 12px;
      margin-top: 12px;
    }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #10141b;
      border: 1px solid #2c3444;
      border-radius: 8px;
      padding: 12px;
      overflow: auto;
    }
    .muted {
      color: #a9b3c4;
    }
    .candidate-actions {
      margin-top: 12px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    .candidate-actions button {
      width: auto;
      min-width: 180px;
      margin-bottom: 0;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Market Signal Desk</h1>
    <div class="subtitle">
      Human-usable source intake and dissemination surface for governed market analysis.
      This page ingests bounded source items, renders normalized signals, surfaces ranked candidate cases,
      and bridges candidates into the governed live analyzer route without creating execution authority.
    </div>

    <div class="grid">
      <div class="card">
        <h2>Source Intake</h2>

        <label>API Key</label>
        <input id="api_key" type="password" placeholder="Required for protected analyzer routes" />

        <label>Request ID</label>
        <input id="request_id" value="sig-001" />

        <label>Source Item ID</label>
        <input id="source_item_id" value="src-001" />

        <label>Source Type</label>
        <select id="source_type">
          <option value="operator_manual">operator_manual</option>
          <option value="newswire">newswire</option>
          <option value="rss_feed">rss_feed</option>
          <option value="watchlist_note">watchlist_note</option>
          <option value="macro_note">macro_note</option>
          <option value="social_observation">social_observation</option>
        </select>

        <label>Headline</label>
        <input id="headline" value="Energy rebound after necessity shock" />

        <label>Body</label>
        <textarea id="body">Refinery disruption appears resolved and energy complex is showing follow-through buying.</textarea>

        <div class="row">
          <div>
            <label>Symbol Hint</label>
            <input id="symbol_hint" value="XLE" />
          </div>
          <div>
            <label>Sector Hint</label>
            <select id="sector_hint">
              <option value="energy" selected>energy</option>
              <option value="materials">materials</option>
              <option value="industrials">industrials</option>
              <option value="utilities">utilities</option>
              <option value="financials">financials</option>
              <option value="technology">technology</option>
              <option value="healthcare">healthcare</option>
              <option value="consumer_staples">consumer_staples</option>
              <option value="consumer_discretionary">consumer_discretionary</option>
              <option value="real_estate">real_estate</option>
              <option value="communication_services">communication_services</option>
              <option value="unknown">unknown</option>
            </select>
          </div>
        </div>

        <div class="row">
          <div>
            <label>Confirmation Hint</label>
            <select id="confirmation_hint">
              <option value="confirmed" selected>confirmed</option>
              <option value="partial">partial</option>
              <option value="missing">missing</option>
              <option value="unknown">unknown</option>
            </select>
          </div>
          <div>
            <label>Price Change %</label>
            <input id="price_change_pct" type="number" step="0.1" value="2.4" />
          </div>
        </div>

        <div class="row">
          <div>
            <label>Source Name</label>
            <input id="source_name" value="Operator Note" />
          </div>
          <div>
            <label>Occurred At</label>
            <input id="occurred_at" value="" />
          </div>
        </div>

        <div class="actions">
          <button type="button" onclick="ingestSignal()">Ingest Source Item</button>
          <button type="button" onclick="loadInbox()">Refresh Inbox</button>
          <button type="button" onclick="resetInbox()">Reset Store</button>
        </div>
      </div>

      <div class="card">
        <h2>Governance State</h2>
        <div class="pill">Advisory Only</div>
        <div class="pill">Execution Blocked</div>
        <div class="pill">Recommendation Logic Unchanged</div>
        <div class="pill">Source Provenance Preserved</div>
        <p class="muted">
          This surface shows signals and candidate suggestions only.
          The candidate bridge submits bounded payloads into the existing governed live analyzer route.
          It does not create trade execution, recommendation mutation, or runtime mutation authority.
        </p>

        <h3>Latest Ingest Result</h3>
        <pre id="latest_result">No source item ingested yet.</pre>
      </div>

      <div class="card full">
        <h2>Incoming Signals</h2>
        <div id="signals_list" class="muted">No signals loaded.</div>
      </div>

      <div class="card full">
        <h2>Candidate Cases</h2>
        <div id="candidates_list" class="muted">No candidate cases loaded.</div>
      </div>

      <div class="card full">
        <h2>Bridge Request</h2>
        <pre id="bridge_request">No candidate bridged yet.</pre>
      </div>

      <div class="card full">
        <h2>Candidate Analysis Result</h2>
        <pre id="analysis_result">No candidate analysis run yet.</pre>
      </div>

      <div class="card full">
        <h2>Raw Inbox Record</h2>
        <pre id="raw_inbox">No inbox loaded.</pre>
      </div>
    </div>
  </div>

  <script>
    async function ingestSignal() {
      const payload = {
        request_id: document.getElementById("request_id").value,
        source_item_id: document.getElementById("source_item_id").value,
        source_type: document.getElementById("source_type").value,
        headline: document.getElementById("headline").value,
        body: document.getElementById("body").value,
        symbol_hint: document.getElementById("symbol_hint").value || null,
        sector_hint: document.getElementById("sector_hint").value,
        confirmation_hint: document.getElementById("confirmation_hint").value,
        price_change_pct: parseFloat(document.getElementById("price_change_pct").value || "0"),
        source_name: document.getElementById("source_name").value || null,
        occurred_at: document.getElementById("occurred_at").value || null,
        tags: []
      };

      const response = await fetch("/market-analyzer/sources/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      document.getElementById("latest_result").textContent = JSON.stringify(data, null, 2);
      await loadInbox();
    }

    async function loadInbox() {
      const response = await fetch("/market-analyzer/sources/inbox");
      const data = await response.json();

      const inbox = data.inbox || {};
      document.getElementById("raw_inbox").textContent = JSON.stringify(data, null, 2);

      const signals = inbox.incoming_signals || [];
      const candidates = inbox.candidate_cases || [];

      renderSignals(signals);
      renderCandidates(candidates);
    }

    async function resetInbox() {
      const response = await fetch("/market-analyzer/sources/reset", { method: "DELETE" });
      const data = await response.json();
      document.getElementById("latest_result").textContent = JSON.stringify(data, null, 2);
      document.getElementById("bridge_request").textContent = "No candidate bridged yet.";
      document.getElementById("analysis_result").textContent = "No candidate analysis run yet.";
      await loadInbox();
    }

    async function analyzeCandidate(candidateId) {
      const bridgeRequestId = "bridge-" + Date.now();
      const bridgeResponse = await fetch("/market-analyzer/sources/analyze-candidate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidateId,
          request_id: bridgeRequestId
        })
      });

      const bridgeData = await bridgeResponse.json();
      document.getElementById("bridge_request").textContent = JSON.stringify(bridgeData, null, 2);

      if (!bridgeResponse.ok) {
        document.getElementById("analysis_result").textContent = JSON.stringify(bridgeData, null, 2);
        return;
      }

      const apiKey = document.getElementById("api_key").value;
      const headers = { "Content-Type": "application/json" };

      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }

      const analysisResponse = await fetch("/market-analyzer/run/live", {
        method: "POST",
        headers,
        body: JSON.stringify(bridgeData.analysis_request)
      });

      const analysisData = await analysisResponse.json();
      document.getElementById("analysis_result").textContent = JSON.stringify(analysisData, null, 2);
    }

    function renderSignals(signals) {
      const host = document.getElementById("signals_list");
      if (!signals.length) {
        host.innerHTML = '<div class="muted">No signals loaded.</div>';
        return;
      }

      host.innerHTML = signals.map(item => `
        <div class="list-item">
          <strong>${escapeHtml(item.headline)}</strong><br/>
          <span class="pill">${escapeHtml(item.source_type)}</span>
          <span class="pill">${escapeHtml(item.event_theme)}</span>
          <span class="pill">${escapeHtml(item.normalized_sector || "unknown")}</span>
          <span class="pill">${escapeHtml(item.normalized_confirmation || "unknown")}</span>
          <div class="muted" style="margin-top: 8px;">
            Symbol: ${escapeHtml(item.normalized_symbol || "none")} |
            Propagation: ${escapeHtml(item.propagation)} |
            Severity: ${escapeHtml(item.severity)}
          </div>
        </div>
      `).join("");
    }

    function renderCandidates(candidates) {
      const host = document.getElementById("candidates_list");
      if (!candidates.length) {
        host.innerHTML = '<div class="muted">No candidate cases loaded.</div>';
        return;
      }

      host.innerHTML = candidates.map(item => `
        <div class="list-item">
          <strong>${escapeHtml(item.symbol || "NO_SYMBOL")} — ${escapeHtml(item.event_theme)}</strong><br/>
          <span class="pill">${escapeHtml(item.suggestion_class)}</span>
          <span class="pill">${escapeHtml(item.sector)}</span>
          <span class="pill">sources: ${escapeHtml(String(item.source_count))}</span>
          <span class="pill">${escapeHtml(item.confirmation_state)}</span>
          <div style="margin-top: 8px;">${escapeHtml(item.suggestion_reason)}</div>
          <div class="muted" style="margin-top: 8px;">
            Propagation: ${escapeHtml(item.propagation)}
          </div>
          <div class="candidate-actions">
            <button type="button" onclick="analyzeCandidate('${escapeJs(item.candidate_id)}')">Analyze Candidate</button>
          </div>
        </div>
      `).join("");
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function escapeJs(value) {
      return String(value).replaceAll("\\\\", "\\\\\\\\").replaceAll("'", "\\\\'");
    }

    loadInbox();
  </script>
</body>
</html>
"""