from __future__ import annotations

from typing import Optional
from datetime import datetime

# Ensure package imports work when running as a script (python backend/main.py)
import sys
from pathlib import Path
import os

import httpx

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

USE_EXTERNAL_INTENT_API = os.getenv("USE_EXTERNAL_INTENT_API", "").lower() in {"1", "true", "yes"}
EXTERNAL_INTENT_API_URL = os.getenv("EXTERNAL_INTENT_API_URL", "").strip()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Use absolute imports so running as a script (`python backend/main.py`) works
# without the "attempted relative import" error.
from backend.db import fetch_history, init_db, log_message
from backend.intents import INTENT_ORDER, INTENTS
from backend.models import ChatRequest, ChatResponse, Message


app = FastAPI(
    title="Mini ChatGPT (Rule-Based)",
    description="A tiny rule-based chatbot to demo intent matching without external APIs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def detect_intent(message: str) -> tuple[str, str, Optional[str], list[str]]:
    """
    Returns (intent, response, matched_keyword, reasoning_steps)
    """
    steps: list[str] = []
    lowered = message.lower()
    steps.append("Converted message to lowercase for simpler matching.")

    for intent_name in INTENT_ORDER:
        if intent_name == "unknown":
            continue
        intent_data = INTENTS[intent_name]
        for keyword in intent_data["keywords"]:
            if keyword in lowered:
                steps.append(f"Found keyword '{keyword}' -> intent '{intent_name}'.")
                return intent_name, intent_data["response"], keyword, steps

    unknown_resp = INTENTS["unknown"]["response"]
    steps.append("No keywords matched. Using fallback intent 'unknown'.")
    return "unknown", unknown_resp, None, steps


def fetch_external_intent(message: str) -> tuple[str, str, Optional[str], list[str]]:
    if not EXTERNAL_INTENT_API_URL:
        raise ValueError("EXTERNAL_INTENT_API_URL is not set")

    steps: list[str] = [f"Calling external intent API: {EXTERNAL_INTENT_API_URL}"]
    with httpx.Client(timeout=6.0) as client:
        resp = client.post(EXTERNAL_INTENT_API_URL, json={"message": message})
        resp.raise_for_status()
        data = resp.json()

    intent = data.get("intent") or "unknown"
    reply = data.get("reply") or data.get("response") or INTENTS["unknown"]["response"]
    matched_keyword = data.get("matched_keyword") or data.get("keyword")

    extra_steps = data.get("steps") or []
    if isinstance(extra_steps, str):
        extra_steps = [extra_steps]
    steps.extend(extra_steps)
    if matched_keyword:
        steps.append(f"External matched keyword: {matched_keyword}")

    return intent, reply, matched_keyword, steps


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/intents")
def list_intents() -> dict[str, dict]:
    return {"intents": INTENTS}


@app.get("/api/history", response_model=list[Message])
def history(limit: int = 50) -> list[Message]:
    rows = fetch_history(limit=limit)
    return [
        Message(
            id=row["id"],
            role=row["role"],  # type: ignore[arg-type]
            content=row["content"],
            intent=row["intent"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    use_external = USE_EXTERNAL_INTENT_API and bool(EXTERNAL_INTENT_API_URL)
    intent = reply = ""
    matched_keyword: Optional[str] = None
    steps: list[str] = []

    if use_external:
        try:
            intent, reply, matched_keyword, steps = fetch_external_intent(message)
        except Exception as exc:  # noqa: BLE001
            # Fall back to dictionary-based intent detection to stay functional.
            fallback_intent, fallback_reply, fallback_kw, fallback_steps = detect_intent(message)
            steps = [
                f"External intent API failed or returned invalid data: {exc}. Falling back to local dictionary."
            ] + fallback_steps
            intent, reply, matched_keyword = fallback_intent, fallback_reply, fallback_kw
    else:
        intent, reply, matched_keyword, steps = detect_intent(message)

    # Persist the exchange so the UI can render history.
    log_message("user", message)
    log_message("bot", reply, intent=intent)

    return ChatResponse(
        reply=reply,
        intent=intent,
        matched_keyword=matched_keyword,
        steps=steps,
        message=message,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

