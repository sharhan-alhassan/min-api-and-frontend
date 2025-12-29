# Mini ChatGPT (Rule-Based)

No external APIs or keys. A FastAPI backend that matches intents from a small
dictionary and a React + Tailwind frontend that looks like ChatGPT.

## Run the backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

## Run the frontend
```bash
cd frontend
npm install
npm run dev
# if the backend runs somewhere else:
# VITE_API_URL=http://localhost:8000 npm run dev
```
