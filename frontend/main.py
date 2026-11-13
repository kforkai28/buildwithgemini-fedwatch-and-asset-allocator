"""FastAPI proxy for deployed FedWatch & Asset Allocator A2A agent.

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the browser).
The proxy authenticates with Application Default Credentials and communicates with the
deployed Agent Runtime over the A2A protocol.
"""

import json
import logging
import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, create_client
from a2a.types import AgentCard, Message, Part, Role, SendMessageRequest
from a2a.utils.constants import PROTOCOL_VERSION_1_0, TransportProtocol, VERSION_HEADER
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.protobuf.json_format import ParseDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend_proxy")

RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/60512894509/locations/us-central1/reasoningEngines/1858659810447196160",
)
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

app = FastAPI()

_creds = None
_auth_request = google.auth.transport.requests.Request()
_card_cache: AgentCard | None = None
_contexts: dict[str, str] = {}


def _get_auth_token() -> str:
    global _creds
    if _creds is None:
        _creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    if not _creds.valid:
        _creds.refresh(_auth_request)
    return _creds.token


async def _get_agent_card() -> AgentCard:
    global _card_cache
    if _card_cache is not None:
        return _card_cache

    token = _get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        VERSION_HEADER: PROTOCOL_VERSION_1_0,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(A2A_CARD_URL, headers=headers)
        resp.raise_for_status()
        card_data = resp.json()

    card = ParseDict(card_data, AgentCard(), ignore_unknown_fields=True)
    # Ensure interfaces point to the public reasoning engine endpoint
    for iface in card.supported_interfaces:
        iface.url = A2A_BASE

    _card_cache = card
    return _card_cache


def _extract_parts(proto_parts) -> list[dict]:
    results = []
    for p in proto_parts:
        if p.text:
            results.append({"kind": "text", "text": p.text})
        elif p.url:
            results.append({"kind": "text", "text": f"\n[File: {p.url}]"})
        elif p.HasField("data"):
            results.append({"kind": "a2ui", "data": json.loads(p.data.value.decode("utf-8")) if hasattr(p.data, "value") else str(p.data)})
    return results


@app.post("/chat")
async def chat(request: Request):
    payload = await request.json()
    user_text = payload.get("message", "").strip()
    if not user_text:
        return JSONResponse({"parts": [{"kind": "text", "text": "Please provide a message."}]})

    client_id = request.client.host if request.client else "default_user"
    context_id = _contexts.get(client_id, "")

    token = _get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        VERSION_HEADER: PROTOCOL_VERSION_1_0,
    }

    card = await _get_agent_card()
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=headers, timeout=120) as http_client:
        config = ClientConfig(
            httpx_client=http_client,
            supported_protocol_bindings=[
                TransportProtocol.JSONRPC,
                TransportProtocol.HTTP_JSON,
            ],
        )
        a2a_client = await create_client(card, config)
        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=user_text)],
            context_id=context_id,
        )

        async for chunk in a2a_client.send_message(SendMessageRequest(message=msg)):
            # Capture context ID for conversational persistence
            if chunk.HasField("artifact_update"):
                if chunk.artifact_update.context_id:
                    _contexts[client_id] = chunk.artifact_update.context_id
                parts.extend(_extract_parts(chunk.artifact_update.artifact.parts))
            elif chunk.HasField("task"):
                if chunk.task.context_id:
                    _contexts[client_id] = chunk.task.context_id
                for artifact in chunk.task.artifacts:
                    parts.extend(_extract_parts(artifact.parts))
            elif chunk.HasField("message"):
                if chunk.message.context_id:
                    _contexts[client_id] = chunk.message.context_id
                parts.extend(_extract_parts(chunk.message.parts))

    if not parts:
        parts = [{"kind": "text", "text": "(The agent did not return a reply.)"}]

    return JSONResponse({"parts": parts})


app.mount("/", StaticFiles(directory="frontend/static" if os.path.isdir("frontend/static") else "static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
