from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure package imports work when running as a script (`python backend/main.py`)
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Use absolute imports so running as a script works without relative-import issues.
from backend.db import init_db  # noqa: E402
from backend.routers.chat_router import ChatRouter  # noqa: E402


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


chat_router = ChatRouter()
app.include_router(
    chat_router.router,
    prefix=chat_router.prefix,
    tags=chat_router.tags,
)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

