from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("FastAPI is required for the demo app. Install with `pip install -e \".[demo]\"`.") from exc

from ..service import extract

app = FastAPI(title="paperfetch demo", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _demo_html()


@app.post("/api/extract")
def api_extract(payload: dict[str, Any]) -> dict[str, Any]:
    input_value = (payload.get("input") or "").strip()
    if not input_value:
        raise HTTPException(status_code=400, detail="`input` is required.")
    enrich_alpha = bool(payload.get("enrich_alpha", True))
    browser = bool(payload.get("browser", False))
    record = extract(input_value, enrich_alpha=enrich_alpha, browser=browser)
    return {"record": record.to_dict(), "markdown": record.to_markdown()}


def _demo_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>paperfetch</title>
  <style>
    :root {
      --bg: #f5efe2;
      --panel: rgba(255, 250, 240, 0.82);
      --panel-strong: #fff8ea;
      --text: #1c1914;
      --muted: #655a4d;
      --line: rgba(28, 25, 20, 0.14);
      --accent: #b74a21;
      --shadow: 0 24px 80px rgba(57, 28, 10, 0.12);
      --radius: 24px;
      font-family: "Space Grotesk", "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(246, 169, 104, 0.32), transparent 30%),
        radial-gradient(circle at 85% 12%, rgba(138, 179, 129, 0.24), transparent 26%),
        linear-gradient(135deg, #efe6d3 0%, #faf6ed 52%, #f0e6d5 100%);
      min-height: 100vh;
    }
    main {
      width: min(1200px, calc(100% - 32px));
      margin: 32px auto;
      display: grid;
      gap: 24px;
    }
    .hero, .panel {
      border: 1px solid var(--line);
      background: var(--panel);
      backdrop-filter: blur(14px);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .hero {
      padding: 28px;
      position: relative;
      overflow: hidden;
    }
    .hero::after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      right: -40px;
      top: -40px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(183, 74, 33, 0.22), transparent 70%);
    }
    h1 {
      margin: 0 0 12px;
      font-size: clamp(2rem, 4vw, 4.6rem);
      line-height: 0.96;
      max-width: 10ch;
    }
    .lede {
      margin: 0;
      max-width: 64ch;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.6;
    }
    .chips {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 18px;
    }
    .chip {
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.64);
      border: 1px solid var(--line);
      font-size: 0.9rem;
      color: var(--muted);
    }
    .grid {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 24px;
    }
    .panel {
      padding: 22px;
    }
    textarea, pre {
      width: 100%;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: var(--panel-strong);
      color: var(--text);
    }
    textarea {
      min-height: 132px;
      resize: vertical;
      padding: 16px;
      font: inherit;
    }
    pre {
      min-height: 420px;
      padding: 16px;
      overflow: auto;
      white-space: pre-wrap;
      line-height: 1.45;
    }
    .controls {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 14px;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      cursor: pointer;
      font: inherit;
      transition: transform 140ms ease, background 140ms ease;
    }
    .primary {
      background: var(--accent);
      color: white;
    }
    .secondary {
      background: rgba(255,255,255,0.7);
      color: var(--text);
      border: 1px solid var(--line);
    }
    button:hover { transform: translateY(-1px); }
    .samples {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }
    .sample {
      padding: 9px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.7);
      cursor: pointer;
      font-size: 0.92rem;
    }
    .meta {
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0 0 12px;
    }
    @media (max-width: 980px) {
      .grid { grid-template-columns: 1fr; }
      h1 { max-width: none; }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <p class="meta">paperfetch / arXiv + alphaXiv unified extractor</p>
      <h1>From paper URL to clean JSON.</h1>
      <p class="lede">
        Paste an arXiv ID, arXiv URL, or alphaXiv URL. The demo returns a structured record and a Markdown dossier
        using the same extraction pipeline as the CLI and Python SDK.
      </p>
      <div class="chips">
        <div class="chip">Canonical metadata from arXiv</div>
        <div class="chip">Metrics and discussion from alphaXiv</div>
        <div class="chip">Provenance included</div>
      </div>
    </section>
    <section class="grid">
      <section class="panel">
        <p class="meta">Input</p>
        <textarea id="input">https://www.alphaxiv.org/abs/2301.12345</textarea>
        <div class="samples">
          <button class="sample" type="button" data-sample="https://www.alphaxiv.org/abs/2301.12345">alphaXiv sample</button>
          <button class="sample" type="button" data-sample="https://arxiv.org/abs/2301.12345">arXiv sample</button>
          <button class="sample" type="button" data-sample="2401.00001">ID sample</button>
        </div>
        <div class="controls">
          <button class="primary" id="run" type="button">Extract</button>
          <button class="secondary" id="copy-json" type="button">Copy JSON</button>
          <button class="secondary" id="copy-md" type="button">Copy Markdown</button>
        </div>
      </section>
      <section class="panel">
        <p class="meta">JSON output</p>
        <pre id="json">{}</pre>
      </section>
    </section>
    <section class="panel">
      <p class="meta">Markdown dossier</p>
      <pre id="markdown">Press Extract to generate the dossier.</pre>
    </section>
  </main>
  <script>
    const input = document.getElementById("input");
    const jsonEl = document.getElementById("json");
    const mdEl = document.getElementById("markdown");

    async function run() {
      jsonEl.textContent = "Loading...";
      mdEl.textContent = "Loading...";
      const response = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: input.value, enrich_alpha: true })
      });
      const payload = await response.json();
      if (!response.ok) {
        const errorText = payload.detail || JSON.stringify(payload, null, 2);
        jsonEl.textContent = errorText;
        mdEl.textContent = errorText;
        return;
      }
      jsonEl.textContent = JSON.stringify(payload.record, null, 2);
      mdEl.textContent = payload.markdown;
    }

    document.getElementById("run").addEventListener("click", run);
    document.getElementById("copy-json").addEventListener("click", () => navigator.clipboard.writeText(jsonEl.textContent));
    document.getElementById("copy-md").addEventListener("click", () => navigator.clipboard.writeText(mdEl.textContent));
    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => {
        input.value = button.dataset.sample;
        run();
      });
    });
    run();
  </script>
</body>
</html>"""
