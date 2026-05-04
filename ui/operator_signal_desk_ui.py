from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def _page_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>AI_GO Signal Desk</title>
  <style>
    :root {
      --bg: #0f1115;
      --panel: #171a21;
      --panel-soft: #1d222b;
      --border: #2b3340;
      --text: #e8edf5;
      --muted: #97a3b6;
      --good: #6dd3a8;
      --warn: #f0c674;
      --bad: #ef6b73;
      --accent: #7aa2ff;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }

    .shell {
      max-width: 1260px;
      margin: 0 auto;
      padding: 24px 18px 40px;
    }

    .header {
      margin-bottom: 20px;
    }

    .title {
      margin: 0 0 6px;
      font-size: 28px;
      font-weight: 700;
    }

    .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }

    .layout {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 18px;
      align-items: start;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }

    .panel-head {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      background: var(--panel-soft);
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .panel-body {
      padding: 16px;
    }

    .field {
      margin-bottom: 14px;
    }

    .field:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    input,
    select,
    textarea,
    button {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #11151b;
      color: var(--text);
      padding: 11px 12px;
      font-size: 14px;
    }

    textarea {
      min-height: 92px;
      resize: vertical;
    }

    .button-row {
      display: flex;
      gap: 10px;
      margin-top: 18px;
    }

    .button-row button {
      cursor: pointer;
      font-weight: 700;
    }

    .button-primary {
      background: var(--accent);
      color: #0b1020;
      border-color: var(--accent);
    }

    .button-secondary {
      background: #121822;
      color: var(--text);
    }

    .stack {
      display: grid;
      gap: 14px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }

    .card.span-2 {
      grid-column: span 2;
    }

    .card-head {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      background: var(--panel-soft);
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.04em;
    }

    .card-body {
      padding: 14px;
    }

    .notice {
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: #121822;
      color: var(--muted);
    }

    .notice.error {
      border-color: rgba(239, 107, 115, 0.4);
      background: rgba(239, 107, 115, 0.08);
      color: #ffd7da;
    }

    .muted {
      color: var(--muted);
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid var(--border);
      background: #121822;
      color: var(--text);
    }

    .badge.good {
      color: var(--good);
      border-color: rgba(109, 211, 168, 0.35);
      background: rgba(109, 211, 168, 0.08);
    }

    .badge.warn {
      color: var(--warn);
      border-color: rgba(240, 198, 116, 0.35);
      background: rgba(240, 198, 116, 0.08);
    }

    .badge.bad {
      color: var(--bad);
      border-color: rgba(239, 107, 115, 0.35);
      background: rgba(239, 107, 115, 0.08);
    }

    .candidate-list,
    .signal-list {
      display: grid;
      gap: 12px;
    }

    .candidate-item,
    .signal-item {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      background: #121822;
    }

    .item-title {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 6px;
    }

    .item-subtitle {
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }

    .item-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }

    .item-actions button {
      width: auto;
      min-width: 120px;
    }

    pre {
      margin: 12px 0 0;
      padding: 12px;
      border-radius: 10px;
      background: #0b0f14;
      border: 1px solid var(--border);
      color: #d7e0ef;
      overflow: auto;
      font-size: 12px;
    }

    details {
      border-top: 1px solid var(--border);
      margin-top: 8px;
      padding-top: 10px;
    }

    summary {
      cursor: pointer;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    @media (max-width: 980px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .grid-2 {
        grid-template-columns: 1fr;
      }

      .card.span-2 {
        grid-column: span 1;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="header">
      <h1 class="title">AI_GO Operator Signal Desk</h1>
      <p class="subtitle">
        Governed source intake and candidate escalation surface for the live analyzer.
      </p>
    </div>

    <div class="layout">
      <section class="panel">
        <div class="panel-head">Manual Source Ingestion</div>
        <div class="panel-body">
          <div id="message" class="notice">
            Ready. Ingest a bounded source item, then review generated candidates.
          </div>

          <form id="ingest-form">
            <div class="field">
              <label for="source-item-id">Source Item ID</label>
              <input id="source-item-id" type="text" value="src-001" />
            </div>

            <div class="field">
              <label for="source-type">Source Type</label>
              <select id="source-type">
                <option value="newswire" selected>newswire</option>
                <option value="operator_note">operator_note</option>
                <option value="research_note">research_note</option>
                <option value="social">social</option>
              </select>
            </div>

            <div class="field">
              <label for="headline">Headline</label>
              <textarea id="headline">Oil infrastructure goes offline after insurgent strike</textarea>
            </div>

            <div class="field">
              <label for="body">Body</label>
              <textarea id="body">Disruption to energy infrastructure may tighten supply and support energy prices.</textarea>
            </div>

            <div class="field">
              <label for="symbol-hint">Symbol Hint</label>
              <input id="symbol-hint" type="text" value="XLE" />
            </div>

            <div class="field">
              <label for="sector-hint">Sector Hint</label>
              <select id="sector-hint">
                <option value="energy" selected>energy</option>
                <option value="materials">materials</option>
                <option value="industrials">industrials</option>
                <option value="utilities">utilities</option>
                <option value="healthcare">healthcare</option>
                <option value="technology">technology</option>
                <option value="consumer">consumer</option>
              </select>
            </div>

            <div class="field">
              <label for="confirmation-hint">Confirmation Hint</label>
              <select id="confirmation-hint">
                <option value="confirmed" selected>confirmed</option>
                <option value="partial">partial</option>
                <option value="missing">missing</option>
              </select>
            </div>

            <div class="field">
              <label for="trust-class">Trust Class</label>
              <select id="trust-class">
                <option value="high" selected>high</option>
                <option value="medium">medium</option>
                <option value="low">low</option>
              </select>
            </div>

            <div class="field">
              <label for="occurred-at">Occurred At</label>
              <input id="occurred-at" type="text" value="2026-03-27T12:00:00Z" />
            </div>

            <div class="field">
              <label for="api-key">API Key (for analyze action)</label>
              <input id="api-key" type="password" placeholder="Required only for analyze-candidate" />
            </div>

            <div class="button-row">
              <button class="button-primary" type="submit">Ingest Source</button>
              <button class="button-secondary" type="button" id="refresh-button">Refresh Desk</button>
              <button class="button-secondary" type="button" id="reset-button">Reset Store</button>
            </div>
          </form>
        </div>
      </section>

      <section class="stack">
        <div class="grid-2">
          <article class="card">
            <div class="card-head">SIGNALS</div>
            <div class="card-body">
              <div id="signals" class="signal-list">
                <div class="muted">No signals loaded yet.</div>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-head">INBOX SUMMARY</div>
            <div class="card-body">
              <div id="inbox-summary" class="muted">No inbox data yet.</div>
            </div>
          </article>

          <article class="card span-2">
            <div class="card-head">CANDIDATES</div>
            <div class="card-body">
              <div id="candidates" class="candidate-list">
                <div class="muted">No candidates loaded yet.</div>
              </div>
            </div>
          </article>

          <article class="card span-2">
            <div class="card-head">LAST ANALYZE RESULT</div>
            <div class="card-body">
              <div id="analysis-result" class="muted">No candidate analyzed yet.</div>
              <details>
                <summary>Show raw analyze response</summary>
                <pre id="raw-analysis">{}</pre>
              </details>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>

  <script>
    function text(value, fallback = "—") {
      if (value === null || value === undefined || value === "") {
        return fallback;
      }
      return String(value);
    }

    function setMessage(message, isError = false) {
      const el = document.getElementById("message");
      el.textContent = message;
      el.className = isError ? "notice error" : "notice";
    }

    function badgeClassForSuggestion(value) {
      const normalized = String(value || "").toLowerCase();
      if (normalized === "analyze") return "good";
      if (normalized === "review") return "warn";
      if (normalized === "dismiss") return "bad";
      return "";
    }

    function badgeClassForConfirmation(value) {
      const normalized = String(value || "").toLowerCase();
      if (normalized === "confirmed") return "good";
      if (normalized === "partial") return "warn";
      if (normalized === "missing") return "bad";
      return "";
    }

    async function getJson(url) {
      const response = await fetch(url);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || data?.message || "Request failed.");
      }
      return data;
    }

    async function postJson(url, payload, apiKey = null) {
      const headers = { "Content-Type": "application/json" };
      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || data?.message || "Request failed.");
      }
      return data;
    }

    async function deleteJson(url) {
      const response = await fetch(url, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || data?.message || "Request failed.");
      }
      return data;
    }

    function renderSignals(signals) {
      const el = document.getElementById("signals");

      if (!signals.length) {
        el.innerHTML = '<div class="muted">No signals available.</div>';
        return;
      }

      el.innerHTML = signals.map(signal => `
        <div class="signal-item">
          <div class="item-title">${text(signal.normalized_symbol, "No symbol")} • ${text(signal.event_theme, "No theme")}</div>
          <div class="item-subtitle">${text(signal.headline || signal.source_item_id, "No headline")}</div>
          <div class="badge-row">
            <span class="badge ${badgeClassForConfirmation(signal.normalized_confirmation)}">Confirmation: ${text(signal.normalized_confirmation)}</span>
            <span class="badge">Sector: ${text(signal.normalized_sector)}</span>
            <span class="badge">Propagation: ${text(signal.propagation)}</span>
            <span class="badge">Severity: ${text(signal.severity)}</span>
            <span class="badge">Trust: ${text(signal.trust_class)}</span>
          </div>
        </div>
      `).join("");
    }

    function renderInboxSummary(inbox) {
      const summary = inbox?.summary || {};
      const el = document.getElementById("inbox-summary");

      el.innerHTML = `
        <div class="badge-row">
          <span class="badge">Signals: ${text(summary.signal_count, "0")}</span>
          <span class="badge">Candidates: ${text(summary.candidate_count, "0")}</span>
          <span class="badge good">Analyze: ${text(summary.analyze_count, "0")}</span>
          <span class="badge warn">Review: ${text(summary.review_count, "0")}</span>
          <span class="badge">Monitor: ${text(summary.monitor_count, "0")}</span>
          <span class="badge bad">Dismiss: ${text(summary.dismiss_count, "0")}</span>
        </div>
      `;
    }

    function renderCandidates(candidates) {
      const el = document.getElementById("candidates");

      if (!candidates.length) {
        el.innerHTML = '<div class="muted">No candidates available.</div>';
        return;
      }

      el.innerHTML = candidates.map((candidate, index) => `
        <div class="candidate-item">
          <div class="item-title">${text(candidate.symbol, "No symbol")} • ${text(candidate.event_theme, "No theme")}</div>
          <div class="item-subtitle">Candidate ID: ${text(candidate.candidate_id)}</div>
          <div class="badge-row">
            <span class="badge ${badgeClassForSuggestion(candidate.suggestion_class)}">Class: ${text(candidate.suggestion_class)}</span>
            <span class="badge ${badgeClassForConfirmation(candidate.confirmation_state)}">Confirmation: ${text(candidate.confirmation_state)}</span>
            <span class="badge">Sources: ${text(candidate.source_count)}</span>
            <span class="badge">Propagation: ${text(candidate.propagation)}</span>
            <span class="badge">Sector: ${text(candidate.sector)}</span>
          </div>
          <div class="item-actions">
            <button class="button-primary" type="button" onclick="analyzeCandidate('${String(candidate.candidate_id).replace(/'/g, "\\'")}', ${index + 1})">
              Analyze Candidate
            </button>
          </div>
        </div>
      `).join("");
    }

    async function loadDesk() {
      const [signalsData, candidatesData, inboxData] = await Promise.all([
        getJson("/market-analyzer/sources/signals"),
        getJson("/market-analyzer/sources/candidates"),
        getJson("/market-analyzer/sources/inbox")
      ]);

      renderSignals(signalsData.signals || []);
      renderCandidates(candidatesData.candidates || []);
      renderInboxSummary(inboxData.inbox || {});
    }

    async function analyzeCandidate(candidateId, ordinal) {
      const apiKey = document.getElementById("api-key").value.trim();
      if (!apiKey) {
        setMessage("API key required for analyze-candidate.", true);
        return;
      }

      const payload = {
        candidate_id: candidateId,
        request_id: `bridge-ui-${ordinal}-${Date.now()}`
      };

      setMessage(`Analyzing candidate ${candidateId}...`);

      try {
        const data = await postJson("/market-analyzer/sources/analyze-candidate", payload, apiKey);
        document.getElementById("analysis-result").innerHTML = `
          <div><strong>Bridge Request ID:</strong> ${text(data.request_id)}</div>
          <div><strong>Symbol:</strong> ${text(data.symbol)}</div>
          <div><strong>Headline:</strong> ${text(data.headline)}</div>
          <div><strong>Sector:</strong> ${text(data.sector)}</div>
          <div><strong>Confirmation:</strong> ${text(data.confirmation)}</div>
          <div><strong>Price Change %:</strong> ${text(data.price_change_pct)}</div>
        `;
        document.getElementById("raw-analysis").textContent = JSON.stringify(data, null, 2);
        setMessage(`Candidate ${candidateId} bridged successfully.`);
      } catch (error) {
        setMessage(error.message || "Analyze request failed.", true);
      }
    }

    document.getElementById("ingest-form").addEventListener("submit", async (event) => {
      event.preventDefault();

      const payload = {
        source_item_id: document.getElementById("source-item-id").value.trim(),
        source_type: document.getElementById("source-type").value,
        headline: document.getElementById("headline").value.trim(),
        body: document.getElementById("body").value.trim(),
        symbol_hint: document.getElementById("symbol-hint").value.trim(),
        sector_hint: document.getElementById("sector-hint").value,
        confirmation_hint: document.getElementById("confirmation-hint").value,
        trust_class: document.getElementById("trust-class").value,
        occurred_at: document.getElementById("occurred-at").value.trim()
      };

      setMessage("Ingesting source item...");

      try {
        await postJson("/market-analyzer/sources/ingest", payload);
        await loadDesk();
        setMessage("Source item ingested.");
      } catch (error) {
        setMessage(error.message || "Source ingest failed.", true);
      }
    });

    document.getElementById("refresh-button").addEventListener("click", async () => {
      setMessage("Refreshing signal desk...");
      try {
        await loadDesk();
        setMessage("Signal desk refreshed.");
      } catch (error) {
        setMessage(error.message || "Refresh failed.", true);
      }
    });

    document.getElementById("reset-button").addEventListener("click", async () => {
      setMessage("Resetting signal store...");
      try {
        await deleteJson("/market-analyzer/sources/reset");
        document.getElementById("analysis-result").innerHTML = '<div class="muted">No candidate analyzed yet.</div>';
        document.getElementById("raw-analysis").textContent = "{}";
        await loadDesk();
        setMessage("Signal store cleared.");
      } catch (error) {
        setMessage(error.message || "Reset failed.", true);
      }
    });

    loadDesk().catch((error) => {
      setMessage(error.message || "Initial signal desk load failed.", true);
    });

    window.analyzeCandidate = analyzeCandidate;
  </script>
</body>
</html>
"""


@router.get("/operator/signal-desk", response_class=HTMLResponse)
def operator_signal_desk_ui() -> HTMLResponse:
    return HTMLResponse(content=_page_html())