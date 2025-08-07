from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

starlette_config = Config(".env")
oauth = OAuth(starlette_config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

async def get_google_user_info(request):
    token = await oauth.google.authorize_access_token(request)
    return token.get("userinfo")
