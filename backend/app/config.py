import os
from dotenv import load_dotenv

load_dotenv(override=True)

APP_NAME = "Jarvis Voice AI Backend"

REDIS_URL = os.getenv("UPSTASH_REDIS_URL")  # Upstash URL
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

REDIS_URL = os.getenv("REDIS_URL")
REDIS_TOKEN = os.getenv("REDIS_TOKEN")

FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", "http://localhost:3000")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")