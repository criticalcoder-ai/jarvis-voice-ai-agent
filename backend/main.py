import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routes.sessions import router as sessions_router
from app.routes.auth import router as auth_router
from app.routes.voice import router as voice_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


app = FastAPI(title="Jarvis Voice AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)


@app.get("/")
def read_root():
    return {"JARVIS": "Just A Rather Very Intelligent System"}

app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(voice_router)
