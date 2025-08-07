from fastapi import Depends, Request, HTTPException, status
from typing import Optional, Tuple
from .jwt_manager import jwt_manager
from app.auth.redis_sessions import is_token_blacklisted
import hashlib

async def get_current_user_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return await jwt_manager.verify_token(token)
    except HTTPException:
        return None



async def get_current_user_required(request: Request) -> dict:
    user = await get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    return user


async def get_user_id_or_guest(request: Request) -> Tuple[Optional[str], str]:
    user = await get_current_user_optional(request)
    if user:
        return user["sub"], user.get("tier", "free")

    seed = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    
    return f"guest_{hashlib.md5(seed.encode()).hexdigest()[:8]}", "guest"
