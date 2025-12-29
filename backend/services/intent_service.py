from __future__ import annotations

import os
from typing import Optional

import httpx

from backend.intents import INTENT_ORDER, INTENTS

# Toggle for optional external intent API.
USE_EXTERNAL_INTENT_API = os.getenv("USE_EXTERNAL_INTENT_API", "").lower() in {"1", "true", "yes"}
EXTERNAL_INTENT_API_URL = os.getenv("EXTERNAL_INTENT_API_URL", "").strip()


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


def should_use_external_intent_api() -> bool:
    return USE_EXTERNAL_INTENT_API and bool(EXTERNAL_INTENT_API_URL)

