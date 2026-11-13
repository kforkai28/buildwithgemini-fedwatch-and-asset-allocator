# FedWatch & Asset Allocator

An institutional macroeconomic strategist and asset allocation advisory agent powered by the **Google Agent Development Kit (ADK)**, **Gemini 2.5**, and the **A2A (Agent-to-Agent) Protocol**.

The agent connects real-time Treasury yield curves and macroeconomic policy indicators with target asset allocation models to provide actionable, regime-adaptive investment guidance.

![FedWatch Rate Hike Scenario Demo](demo_rate_hike_scenario.gif)

---

## What the Agent Actually Does

The agent operates as a ReAct macro advisor with high-level multi-step reasoning (`ThinkingConfig(thinking_level=HIGH)`). When queried, it synthesizes market data, consults macroeconomic databases, recommends target portfolio weights, and generates visual infographics.

### Implemented Tools & Google Cloud Services

Based on `app/agent.py`, `app/firestore_tools.py`, `app/market_tools.py`, and `app/image_tools.py`, here are the tools and services wired into this agent:

| Capability | Tool Function | Backing Service / Library | Status |
| :--- | :--- | :--- | :--- |
| **Live Treasury Yields** | `fetch_live_treasury_yields` | `yfinance` (zero external key required) | **Active** |
| **Macro Indicators Catalog** | `get_macro_indicator`<br>`list_macro_indicators`<br>`update_macro_indicator` | **Google Cloud Firestore** (`macro_indicators` collection) | **Active** |
| **Portfolio Models** | `get_portfolio_model`<br>`list_portfolio_models` | **Google Cloud Firestore** (`portfolio_models` collection) | **Active** |
| **User Portfolio Persistence** | `save_user_portfolio_allocation` | **Google Cloud Firestore** (`user_portfolios` collection) | **Active** |
| **Multimodal Infographics** | `generate_macro_infographic` | **Vertex AI Imagen** (`gemini-2.5-flash-image`) + **Google Cloud Storage** | **Active** |
| **St. Louis Fed Series** | `fetch_fred_macro_series` | St. Louis Fed FRED API | **Active** *(Optional key; graceful fallback)* |
| **Interactive Donut Charts** | Dynamic frontend renderer | Client-side **Chart.js** in terminal UI | **Active** |
| **Agent Interoperability** | A2A Protocol v1.0 | `@a2a-ai/client` / httpx A2A streaming | **Active** |

### Planned / Not Yet Implemented
* **Cross-Session Vertex AI Memory Bank:** *Planned, not yet implemented.* Sessions currently use in-memory state (`session_type: in_memory` in `agents-cli-manifest.yaml`).
* **Python Code Sandbox Execution:** *Planned, not yet implemented.* Quantitative stress-testing runs via local tool calculations.
* **Agent Engine A2UI Card Projection:** *Planned, not yet implemented.* Rich UI tables and interactive donut charts are currently rendered client-side in the web frontend.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Web Chat Terminal                    │
│    (FastAPI Proxy + Interleaved Chart.js Renderers)    │
└───────────────────────────┬────────────────────────────┘
                            │ A2A Protocol (Streaming)
┌───────────────────────────▼────────────────────────────┐
│          Google Vertex AI Agent Runtime (ADK)          │
│               Model: gemini-2.5-flash                  │
│       Reasoning: ThinkingConfig (HIGH level)           │
└──────┬────────────────────┬────────────────────┬───────┘
       │                    │                    │
┌──────▼───────┐     ┌──────▼───────┐     ┌──────▼───────┐
│ Market Data  │     │  Firestore   │     │ Cloud Storage│
│  Live Yields │     │ Macro Trends │     │ Infographics │
│ (3M, 5Y, 10Y)│     │ & Portfolios │     │  & Assets    │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## Local Setup & Development

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud SDK (`gcloud`) authenticated to your GCP project
- Node.js & Playwright (only if re-recording demo videos)

### 2. Installation
Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/kforkai28/buildwithgemini-fedwatch-and-asset-allocator.git
cd buildwithgemini-fedwatch-and-asset-allocator
uv sync
```

### 3. Environment Configuration
Create a `.env` file in the project root:

```bash
GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
GOOGLE_CLOUD_REGION="us-central1"
# Optional: St. Louis Fed FRED API key
# FRED_API_KEY="your-fred-api-key"
```

Seed initial portfolio templates and macro indicators to Firestore:

```bash
uv run python seed_firestore.py
```

### 4. Running the Agent Locally

#### Option A: ADK Developer Playground
Run the local ADK developer UI with live hot-reloading:

```bash
uv run adk web --host 0.0.0.0 --port 8000 --reload_agents app
```

#### Option B: Standalone Web Chat Terminal
Launch the FastAPI web server hosting the terminal:

```bash
export PORT=8080
uv run python frontend/main.py
```

---

## Evaluation & Testing

Run the test suite and pre-flight evaluation against the macro benchmark dataset:

```bash
# Run unit and integration tests
uv run pytest tests/unit tests/integration

# Run pre-flight LLM evaluation
agents-cli eval --dataset eval_dataset.json
```

---

## Deployment Instructions

### Deploy Agent to Vertex AI Agent Runtime

```bash
agents-cli deploy --region us-central1
```

### Deploy Web Chat Frontend to Cloud Run

```bash
gcloud run deploy fedwatch-frontend \
  --source frontend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars AGENT_DIRECTORY="app"
```

---

## 🌐 Replicating Outside Google Cloud Environment

For AI agents or developers running this codebase outside of Google Cloud Platform (e.g. on AWS, Azure, local workstations, or alternative cloud providers), follow this replication guide:

### 1. Model Provider Adaptation
* **Default Setup:** Uses `gemini-2.5-flash` via `google.adk.models.Gemini` with Vertex AI backend.
* **Non-GCP Gemini Access:** Set `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/) and initialize `genai.Client(api_key=os.environ["GEMINI_API_KEY"])` rather than relying on GCP Application Default Credentials (`ADC`).
* **Framework Translation:** The system prompt, ReAct flow, and tool schemas in [`app/agent.py`](app/agent.py) map directly to LangChain (`ChatGoogleGenerativeAI` / `create_react_agent`), LlamaIndex, or AutoGen.

### 2. Market Data Tools (Zero GCP Dependencies)
* [`fetch_live_treasury_yields`](app/market_tools.py) uses `yfinance` to scrape US Treasury benchmarks (`^IRX`, `^FVX`, `^TNX`, `^TYX`). It has **zero GCP dependencies** and works out-of-the-box in any standard Python environment.
* [`fetch_fred_macro_series`](app/market_tools.py) interacts directly with the St. Louis Fed HTTP API. Set `export FRED_API_KEY="..."` to enable official economic data queries anywhere.

### 3. Replacing Google Cloud Firestore
* **In-Memory / SQLite Fallback:** [`app/firestore_tools.py`](app/firestore_tools.py) can be swapped for a local SQLite or PostgreSQL database.
* **Firestore Local Emulator:** Run the official Firestore emulator via Docker:
  ```bash
  docker run -d -p 8080:8080 -e FIRESTORE_PROJECT_ID="local-fedwatch" google/cloud-sdk:emulators gcloud beta emulators firestore start --host-port=0.0.0.0:8080
  export FIRESTORE_EMULATOR_HOST="localhost:8080"
  ```
  When `FIRESTORE_EMULATOR_HOST` is defined, `google-cloud-firestore` automatically routes queries locally without authentication.
* **Document Schema Reference:**
  * `macro_indicators/{id}`: `{ id: str, current_value: float, trend: str, fomc_stance: str, summary: str }`
  * `portfolio_models/{id}`: `{ id: str, name: str, risk_profile: str, target_allocations: map, target_duration: str, rationale: str }`
  * `user_portfolios/{user_id}`: `{ user_id: str, portfolio_name: str, risk_level: str, allocations: map, notes: str }`

### 4. Replacing Cloud Storage & Imagen
* **Local File System / S3 / MinIO:** In [`app/image_tools.py`](app/image_tools.py), replace `storage.Client` with standard disk writes (`open(f"static/infographics/{uuid}.png", "wb")`) or an AWS S3/MinIO bucket.
* **Alternative Image Generators:** If Vertex AI Imagen isn't accessible, swap the image call with standard Stable Diffusion, DALL-E 3 (`openai.images.generate`), or client-side chart generation (e.g., Python `matplotlib` / `seaborn` returning static PNGs).

### 5. Running the Complete Self-Contained Stack
```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
export GEMINI_API_KEY="your-gemini-api-key"
export FIRESTORE_EMULATOR_HOST="localhost:8080"

# 3. Seed local store
uv run python seed_firestore.py

# 4. Launch terminal frontend
export PORT=8080
uv run python frontend/main.py
```

---

## License
Licensed under the Apache License, Version 2.0.
