# Mini ChatGPT Backend (FastAPI)

Rule-based chatbot API. No external APIs or keys required.

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

## API

- `POST /api/chat` – body: `{"message": "hi"}`. Returns intent, reply, matched keyword, and reasoning steps.
- `GET /api/history` – recent user/bot turns from SQLite (`data/chat.db`).
- `GET /api/intents` – current intent dictionary.
- `GET /api/health` – simple status check.

## Optional: external intent API toggle

Set env vars to prefer an external endpoint over the local dictionary:

```bash
USE_EXTERNAL_INTENT_API=true
EXTERNAL_INTENT_API_URL=https://example.com/intent
```

The external endpoint should accept `{"message": "<text>"}` and return JSON with
`reply`, `intent`, and optionally `matched_keyword` and `steps`. If the request
fails or the data is malformed, the app falls back to the built-in dictionary so
the bot keeps working.

