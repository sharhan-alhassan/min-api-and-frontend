from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Literal, TypedDict


DB_PATH = Path(__file__).resolve().parent / "data" / "chat.db"


class MessageRow(TypedDict):
    id: int
    role: Literal["user", "bot"]
    content: str
    intent: str | None
    created_at: str


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
                content TEXT NOT NULL,
                intent TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def log_message(role: Literal["user", "bot"], content: str, intent: str | None = None) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (role, content, intent) VALUES (?, ?, ?)",
            (role, content, intent),
        )
        conn.commit()


def fetch_history(limit: int = 50) -> list[MessageRow]:
    with _connect() as conn:
        rows: list[sqlite3.Row] = conn.execute(
            """
            SELECT id, role, content, intent, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    history: list[MessageRow] = [
        MessageRow(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            intent=row["intent"],
            created_at=row["created_at"],
        )
        for row in rows
    ]

    return history[::-1]  # return oldest-first

