from pathlib import Path
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

BASE_DIR = Path(__file__).resolve().parent.parent  # Goes from backend/ → jarvis-voice-agent/
env_path = BASE_DIR / ".env"
config = Config(env_file=str(env_path))

oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

async def get_google_user_info(request):
    token = await oauth.google.authorize_access_token(request)
    return token.get("userinfo")
