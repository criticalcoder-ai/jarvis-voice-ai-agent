# app/routes/sessions.py
from fastapi import APIRouter, Depends, Request, HTTPException
from uuid import uuid4
import logging

from app.auth.dependencies import get_user_id_or_guest
from app.services.access_control import access_control
from app.services.exceptions import TierNotFoundError, LimitExceededError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create")
async def create_session(request: Request, user_info=Depends(get_user_id_or_guest)):
    """
    Create a new voice/chat session for the user.
    Applies tier-based access control rules and returns a session ID.
    """
    user_id, tier = user_info
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    logger.info(f"Session create request from {user_id} ({tier}) | IP: {client_ip} | UA: {user_agent}")

    try:
        # Check tier & usage permissions
        check = await access_control.check_permission(user_id, tier)
        if not check.allowed:
            raise HTTPException(
                status_code=403,
                detail={"reason": check.reason, "action": check.action}
            )

        # Generate unique session ID
        session_id = str(uuid4())

        # Track session in Redis
        await access_control.start_session(user_id, session_id)

        # TODO: Replace with LiveKit/JWT session token generation
        return {
            "session_id": session_id,
            "tier": tier,
            "ip": client_ip,
            "user_agent": user_agent
        }

    except TierNotFoundError as e:
        logger.warning(f"Tier not found for user {user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except LimitExceededError as e:
        logger.info(f"Limit exceeded for user {user_id}: {e}")
        raise HTTPException(status_code=403, detail=str(e))

    except Exception as e:
        logger.exception(f"Unexpected error creating session for {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
