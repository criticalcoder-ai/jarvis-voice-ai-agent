import os
from dotenv import load_dotenv

load_dotenv(override=True)

APP_NAME = "Jarvis Voice AI Backend"
REDIS_URL = os.getenv("REDIS_URL")  # Upstash URL
REDIS_TOKEN = os.getenv("REDIS_TOKEN")
JWT_SECRET = os.getenv("JWT_SECRET",)
JWT_ALGORITHM = "HS256"
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

DATABASE_URL = os.getenv("DATABASE_URL")