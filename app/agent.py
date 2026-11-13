# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.firestore_tools import (
    get_macro_indicator,
    list_macro_indicators,
    update_macro_indicator,
    get_portfolio_model,
    list_portfolio_models,
    save_user_portfolio_allocation,
)
from app.market_tools import (
    fetch_live_treasury_yields,
    fetch_fred_macro_series,
)
from app.image_tools import generate_macro_infographic

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """You are the FedWatch & Asset Allocator agent.
Your primary role is to serve as an institutional macro strategist and financial advisor:
1. Macro Monitoring: Retrieve current Treasury yields across the curve and query macroeconomic indicators (Fed Funds, Core PCE, Unemployment, Yield Curve spreads).
2. FOMC Contextualization: Analyze hawkish vs dovish policy postures, rate expectations, and yield curve shifts (steepening vs inversion).
3. Asset Allocation: Recommend tactical portfolio models (conservative income, balanced growth, macro momentum) aligned with current macro conditions and user risk tolerance.
4. Response Format:
   - ALWAYS provide a clear, beautifully structured markdown conversational reply in the chat.
   - Use clean tables, bold metrics, bullet points, and section headers to present macro rates, spreads, and portfolio weights.
   - When tools return data, immediately synthesize and interpret the results in your natural language response.
5. Tool Guidance:
   - For live Treasury yields and 10Y-3M spreads, ALWAYS call `fetch_live_treasury_yields()`.
   - For stored macro indicators and FOMC posture summaries, use `get_macro_indicator()` or `list_macro_indicators()`.
   - For portfolio models and target asset weights, use `get_portfolio_model()` or `list_portfolio_models()`.
   - If user asks for deep official Fed economic series (e.g., FRED data like balance sheet QT or Core PCE), use `fetch_fred_macro_series()`. If no key is configured, politely explain how to set FRED_API_KEY while noting that live yields are fully operational via market data.
   - When users request a chart, visual graphic, or diagram, call `generate_macro_infographic(prompt=...)` and embed the returned image URL using markdown `![Infographic](image_url)`.
   - When users decide on an allocation, persist it using `save_user_portfolio_allocation()`.
6. Guardrails: Remind users that macroeconomic scenarios and model allocations are for educational and strategic analysis purposes."""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
        generate_content_config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.HIGH,
                include_thoughts=True,
            )
        ),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        fetch_live_treasury_yields,
        fetch_fred_macro_series,
        get_macro_indicator,
        list_macro_indicators,
        update_macro_indicator,
        get_portfolio_model,
        list_portfolio_models,
        save_user_portfolio_allocation,
        generate_macro_infographic,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
