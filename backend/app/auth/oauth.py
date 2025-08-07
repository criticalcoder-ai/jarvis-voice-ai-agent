from pathlib import Path
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Get base directory: backend/
BASE_DIR = Path(__file__).resolve().parents[3]
config = Config(BASE_DIR / ".env")

oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

async def get_google_user_info(request):
    token = await oauth.google.authorize_access_token(request)
    return token.get("userinfo")
