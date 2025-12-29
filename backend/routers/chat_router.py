from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.db import fetch_history, log_message
from backend.intents import INTENTS
from backend.models import ChatRequest, ChatResponse, Message
from backend.services.intent_service import (
    detect_intent,
    fetch_external_intent,
    should_use_external_intent_api,
)


class ChatRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.prefix = "/api"
        self.tags: list[str | Enum] = ["chat"]

        self.router.add_api_route(
            "/health",
            self.health,
            methods=["GET"],
            summary="Health check",
        )
        self.router.add_api_route(
            "/intents",
            self.list_intents,
            methods=["GET"],
            summary="List intents",
        )
        self.router.add_api_route(
            "/history",
            self.history,
            methods=["GET"],
            response_model=list[Message],
            summary="Conversation history",
        )
        self.router.add_api_route(
            "/chat",
            self.chat,
            methods=["POST"],
            response_model=ChatResponse,
            summary="Chat with the bot",
        )

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_intents(self) -> dict[str, dict]:
        return {"intents": INTENTS}

    def history(self, limit: int = 50) -> list[Message]:
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

    def chat(self, body: ChatRequest) -> ChatResponse:
        message = body.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        use_external = should_use_external_intent_api()
        intent = reply = ""
        matched_keyword: Optional[str] = None
        steps: list[str] = []

        if use_external:
            try:
                intent, reply, matched_keyword, steps = fetch_external_intent(message)
            except Exception as exc:  # noqa: BLE001
                fallback_intent, fallback_reply, fallback_kw, fallback_steps = detect_intent(message)
                steps = [
                    f"External intent API failed or returned invalid data: {exc}. Falling back to local dictionary."
                ] + fallback_steps
                intent, reply, matched_keyword = fallback_intent, fallback_reply, fallback_kw
        else:
            intent, reply, matched_keyword, steps = detect_intent(message)

        log_message("user", message)
        log_message("bot", reply, intent=intent)

        return ChatResponse(
            reply=reply,
            intent=intent,
            matched_keyword=matched_keyword,
            steps=steps,
            message=message,
        )

