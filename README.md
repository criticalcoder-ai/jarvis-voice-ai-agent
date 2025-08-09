# Jarvis Voice Agent (Under Development)

A real-time AI voice assistant split into two Python services with isolated environments:
- backend: FastAPI REST API for auth, sessions, and LiveKit room management
- worker: LiveKit Agent that runs STT → LLM → TTS for live voice conversations

## Project split
- Backend (FastAPI)
  - Auth (Google OAuth + JWT), session/tier control, LiveKit token/room handling
- Worker (LiveKit Agent)
  - Deepgram STT, OpenRouter LLM (e.g., Gemini/GPT), Google Cloud TTS, Silero VAD

## Basic structure
```
jarvis-voice-agent/
├─ backend/
│  ├─ main.py
│  └─ app/{auth,db,routes,schemas,services}
├─ worker/
│  ├─ main.py
│  ├─ entry.py
│  └─ agent.py
└─ google-creds.json (gitignored)
```

## Prerequisites
- Python 3.13+
- uv (Python package manager) installed
- Required service credentials in .env and google-creds.json

## Setup and run with uv (isolated per service)
Run each service in its own terminal (separate virtual envs and processes).

- Backend (Terminal 1)
```powershell
cd backend
uv venv
.venv\Scripts\Activate.ps1
uv sync
uv run uvicorn main:app --reload --port 8000
```

- Worker (Terminal 2)
```powershell
cd worker
uv venv
.venv\Scripts\Activate.ps1
uv sync
uv run python main.py dev
```

## Environment
Place environment variables in a .env at the repo root (used by both services):
- DATABASE_URL, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN
- LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL
- JWT_SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
- DEEPGRAM_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, ELEVENLABS_API_KEY
- GOOGLE_APPLICATION_CREDENTIALS=./google-creds.json

API docs: http://localhost:8000/docs (after backend starts)

Status: actively under development.
