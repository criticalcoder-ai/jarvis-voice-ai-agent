from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
import app.config as config
from app.auth.redis_sessions import is_token_blacklisted


class JWTManager:
    def __init__(self):
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.expire_minutes = config.JWT_EXPIRE_MINUTES

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """ Create a JWT access token for a user. """
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        token_data = {
            "sub": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("profile_pic"),
            "tier": user_data.get("tier", "free"),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and check if it's blacklisted."""

        if await is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked. Please log in again.",
            )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    def cookie_settings(self):
        """ Get cookie settings for a JWT token. """
        return {
            "httponly": True,
            "secure": True,
            "samesite": "lax",
            "max_age": self.expire_minutes * 60,
            "path": "/",
            "domain":"." + config.FRONTEND_DOMAIN,
        }


jwt_manager = JWTManager()
