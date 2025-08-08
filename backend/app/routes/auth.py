from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import json
import logging
import app.config as config

from app.auth.jwt_manager import jwt_manager
from app.auth.dependencies import get_current_user_required
from app.auth.oauth import oauth, get_google_user_info
from app.db.connection import get_db_connection
from app.db.users import get_or_create_user, get_user_by_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def login(request: Request):
    try:
        redirect_uri = request.url_for("auth_callback")
        redirect_origin = request.query_params.get(
            "redirect_origin", config.FRONTEND_DOMAIN
        )
        
        state = json.dumps({"redirect_origin": redirect_origin})
        
        return await oauth.google.authorize_redirect(request, redirect_uri, state=state)
    
    except Exception:
        logger.exception("Error during Google login redirect")
        raise HTTPException(
            status_code=500, detail="Google login failed. Please try again."
        )


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    try:
        user_info = await get_google_user_info(request)
        email = user_info["email"]
        name = user_info.get("name", "")
        picture = user_info.get("picture", "")

        async with get_db_connection() as conn:
            user = await get_or_create_user(conn, email, name, picture)

        token = jwt_manager.create_access_token(user)

        # Read redirect origin
        state_str = request.query_params.get("state", "{}")
        
        try:
            state_data = json.loads(state_str)
        except json.JSONDecodeError:
            state_data = {}
            
        redirect_origin = state_data.get("redirect_origin", config.FRONTEND_DOMAIN)

        response = RedirectResponse(url=f"{redirect_origin}/")
        
        response.set_cookie(
            key="access_token", value=token, **jwt_manager.cookie_settings()
        )
        return response
    
    except Exception:
        logger.exception("Error during OAuth callback")
        raise HTTPException(
            status_code=500, detail="Authentication failed. Please try again."
        )


@router.get("/validate")
async def validate_token(user=Depends(get_current_user_required)):
    return {"status": "valid", "user_id": user.get("sub")}


@router.get("/user")
async def get_user_info(user=Depends(get_current_user_required)):
    async with get_db_connection() as conn:
        db_user = await get_user_by_id(conn, user.get("sub"))
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
