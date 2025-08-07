from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
import app.auth.config as config

class JWTManager:
    def __init__(self):
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.expire_minutes = config.JWT_EXPIRE_MINUTES

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        token_data = {
            "sub": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("profile_pic"),
            "tier": user_data.get("tier", "free"),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int(expire.timestamp())
        }
        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    def cookie_settings(self):
        return {
            "httponly": True,
            "secure": True,
            "samesite": "lax",
            "max_age": self.expire_minutes * 60,
            "path": "/"
        }

jwt_manager = JWTManager()
