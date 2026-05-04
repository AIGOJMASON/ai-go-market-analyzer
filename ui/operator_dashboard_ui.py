from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def get_operator_dashboard_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI_GO Market Board</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #121933;
      --panel-2: #182243;
      --panel-3: #0f1730;
      --text: #edf2ff;
      --muted: #a9b5d1;
      --accent: #7aa2ff;
      --accent-2: #4fd1c5;
      --border: #2a3763;
      --shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
      --radius: 14px;
      --radius-sm: 12px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Inter, Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #0b1020 0%, #0f1730 100%);
      color: var(--text);
    }

    .page {
      max-width: 1380px;
      margin: 0 auto;
      padding: 28px 20px 48px;
    }

    .hero {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      margin-bottom: 18px;
    }

    .hero-copy h1 {
      margin: 0 0 10px;
      font-size: 32px;
      line-height: 1.1;
      letter-spacing: -0.02em;
    }

    .hero-copy p {
      margin: 0;
      color: var(--muted);
      max-width: 760px;
      line-height: 1.55;
      font-size: 15px;
    }

    .hero-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    button,
    a.link-button {
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      cursor: pointer;
      transition: background 0.18s ease, transform 0.18s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
    }

    button:hover,
    a.link-button:hover {
      background: #22305c;
      transform: translateY(-1px);
    }

    .status-banner {
      margin-bottom: 18px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: rgba(24, 34, 67, 0.65);
      color: var(--muted);
      box-shadow: var(--shadow);
      line-height: 1.5;
    }

    .status-chip-row {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .status-chip {
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: rgba(18, 25, 51, 0.95);
      box-shadow: var(--shadow);
      padding: 12px 14px;
    }

    .status-chip-label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .status-chip-value {
      display: block;
      font-size: 15px;
      color: var(--text);
      line-height: 1.4;
    }

    .board-card {
      border: 1px solid var(--border);
      background: rgba(18, 25, 51, 0.95);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .board-card-header {
      padding: 16px 18px 12px;
      border-bottom: 1px solid rgba(122, 162, 255, 0.12);
      background: linear-gradient(180deg, rgba(27, 39, 77, 0.65), rgba(18, 25, 51, 0.2));
    }

    .board-card-header h2 {
      margin: 0 0 6px;
      font-size: 18px;
      letter-spacing: -0.01em;
    }

    .board-card-header p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
      font-size: 14px;
    }

    .board-card-body {
      padding: 18px;
    }

    .summary-card {
      margin-bottom: 18px;
    }

    .summary-line {
      margin: 0 0 10px;
      font-size: 18px;
      line-height: 1.6;
      color: var(--text);
    }

    .support-text {
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 14px;
    }

    .indicator-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }

    .indicator-card {
      border: 1px solid var(--border);
      background: rgba(18, 25, 51, 0.95);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 16px;
      min-height: 270px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .indicator-card.placeholder {
      opacity: 0.88;
    }

    .indicator-card.commodities {
      grid-column: span 2;
    }

    .indicator-header {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }

    .indicator-symbol {
      font-size: 13px;
      color: var(--accent-2);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 5px;
    }

    .indicator-name {
      font-size: 16px;
      line-height: 1.4;
      color: var(--text);
    }

    .indicator-badge {
      border: 1px solid rgba(122, 162, 255, 0.2);
      background: rgba(122, 162, 255, 0.12);
      color: var(--text);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      white-space: nowrap;
    }

    .indicator-badge.muted {
      background: rgba(255, 255, 255, 0.05);
      color: var(--muted);
    }

    .indicator-section {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .section-label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .section-value {
      font-size: 14px;
      line-height: 1.55;
      color: var(--text);
    }

    .main-grid {
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .secondary-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .metric-grid {
      display: grid;
      gap: 12px;
    }

    .metric-grid.three-up {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 14px;
    }

    .metric-box {
      padding: 12px 13px;
      border: 1px solid rgba(122, 162, 255, 0.12);
      border-radius: 12px;
      background: rgba(11, 16, 32, 0.36);
    }

    .metric-label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .metric-value {
      display: block;
      color: var(--text);
      font-size: 15px;
      line-height: 1.45;
    }

    .symbol-list {
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 10px;
    }

    .symbol-list-item {
      border: 1px solid rgba(122, 162, 255, 0.1);
      border-radius: 12px;
      background: rgba(11, 16, 32, 0.28);
      padding: 12px 13px;
    }

    .symbol-row {
      display: flex;
      gap: 10px;
      align-items: flex-start;
      flex-wrap: wrap;
    }

    .symbol-pill {
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(79, 209, 197, 0.12);
      color: var(--text);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .symbol-note {
      color: var(--text);
      line-height: 1.55;
      font-size: 14px;
      flex: 1;
      min-width: 180px;
    }

    .trigger-grid {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr;
    }

    .trigger-grid.compact {
      grid-template-columns: 1fr;
    }

    .trigger-block {
      border: 1px solid rgba(122, 162, 255, 0.1);
      border-radius: 12px;
      background: rgba(11, 16, 32, 0.28);
      padding: 12px 13px;
    }

    .trigger-block.compact {
      padding: 10px 12px;
    }

    .trigger-label {
      display: block;
      margin-bottom: 6px;
      color: var(--accent-2);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .trigger-text {
      color: var(--text);
      font-size: 14px;
      line-height: 1.55;
    }

    .commodity-board {
      display: grid;
      gap: 8px;
      margin-top: 4px;
    }

    .commodity-row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid rgba(122, 162, 255, 0.08);
    }

    .commodity-row:last-child {
      border-bottom: none;
    }

    .commodity-name {
      color: var(--text);
      font-size: 14px;
      line-height: 1.4;
    }

    .commodity-move {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.4;
      white-space: nowrap;
    }

    .commodity-summary,
    .commodity-watch {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .tag-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      background: rgba(122, 162, 255, 0.12);
      border: 1px solid rgba(122, 162, 255, 0.16);
      color: var(--text);
      font-size: 12px;
      line-height: 1.2;
    }

    .empty-state {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }

    .governance-footer {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .footer-metric {
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: rgba(18, 25, 51, 0.95);
      box-shadow: var(--shadow);
      padding: 12px 14px;
    }

    .footer-label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .footer-value {
      display: block;
      font-size: 15px;
      color: var(--text);
      line-height: 1.4;
    }

    .raw-panel {
      margin-top: 20px;
      border-top: 1px solid rgba(122, 162, 255, 0.12);
      padding-top: 20px;
    }

    .raw-panel pre {
      margin: 0;
      padding: 16px;
      border-radius: 12px;
      background: #09101f;
      border: 1px solid rgba(122, 162, 255, 0.12);
      overflow: auto;
      color: #dbe6ff;
      font-size: 13px;
      line-height: 1.5;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 1180px) {
      .indicator-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .indicator-card.commodities {
        grid-column: span 2;
      }

      .main-grid,
      .secondary-grid,
      .status-chip-row,
      .governance-footer {
        grid-template-columns: 1fr;
      }

      .metric-grid.three-up {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 780px) {
      .hero {
        flex-direction: column;
      }

      .hero-actions {
        justify-content: flex-start;
      }

      .indicator-grid {
        grid-template-columns: 1fr;
      }

      .indicator-card.commodities {
        grid-column: span 1;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="hero-copy">
        <h1>AI_GO Market Board</h1>
        <p>
          Governed market read from live signal, historical outcomes, and recent memory.
          This surface is designed to show the market structure first, then the most relevant actions and watch conditions.
        </p>
      </div>

      <div class="hero-actions">
        <button id="refresh-live-view" type="button">Refresh Latest View</button>
        <button id="toggle-raw-response" type="button">Show Raw Response</button>
        <a id="full-analysis-link" class="link-button" href="/market-analyzer/operator/latest" target="_blank" rel="noopener noreferrer">
          View Full Analysis
        </a>
      </div>
    </section>

    <section class="status-banner" id="dashboard-status">
      Waiting for the latest market board payload.
    </section>

    <section class="status-chip-row" id="status-chip-row"></section>

    <section id="board-summary"></section>

    <section class="indicator-grid" id="indicator-grid"></section>

    <section class="main-grid">
      <div id="top-buys-slot"></div>
      <div id="watch-triggers-slot"></div>
    </section>

    <section class="secondary-grid">
      <div id="historical-read-slot"></div>
      <div id="recent-memory-slot"></div>
    </section>

    <section class="governance-footer" id="governance-footer"></section>

    <section class="board-card raw-panel hidden" id="raw-response-panel">
      <div class="board-card-header">
        <h2>Raw Response</h2>
        <p>Latest governed payload for debugging and verification.</p>
      </div>
      <div class="board-card-body">
        <pre id="raw-response-content">{}</pre>
      </div>
    </section>
  </main>

  <script>
    window.__AI_GO_OPERATOR_INITIAL_PAYLOAD__ = null;
  </script>
  <script src="/static/operator_dashboard_transform.js?v=20260410b"></script>
</body>
</html>
""".strip()


def render_operator_dashboard_ui() -> HTMLResponse:
    return HTMLResponse(content=get_operator_dashboard_html())


def build_operator_dashboard_ui_response() -> HTMLResponse:
    return render_operator_dashboard_ui()


@router.get("/operator", response_class=HTMLResponse)
def operator_dashboard() -> HTMLResponse:
    return render_operator_dashboard_ui()