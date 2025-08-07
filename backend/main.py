from fastapi import FastAPI
from app.routes import sessions, auth

app = FastAPI(title="Jarvis Voice AI Backend")

app.include_router(auth.router)
app.include_router(sessions.router)
