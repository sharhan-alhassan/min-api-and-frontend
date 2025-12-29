from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message to the bot")


class ChatResponse(BaseModel):
    reply: str
    intent: str
    matched_keyword: Optional[str] = None
    steps: list[str]
    message: str


class Message(BaseModel):
    id: int
    role: Literal["user", "bot"]
    content: str
    intent: Optional[str] = None
    created_at: datetime

