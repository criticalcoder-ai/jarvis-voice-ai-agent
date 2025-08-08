# app/routes/sessions.py
import json
from fastapi import APIRouter, Depends, Request, HTTPException, status
from uuid import uuid4
import logging
from app.auth.dependencies import get_user_id_or_guest
from app.schemas.sessions import CreateSessionRequest, EndSessionRequest
from app.services.redis_client import redis_client
from app.services.access_control import access_control
from app.services.exceptions import TierNotFoundError, LimitExceededError
from app.services.livekit import livekit_service
from app.voice_config import get_voice_by_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: Request,
    body: CreateSessionRequest,
    user_info=Depends(get_user_id_or_guest),
):
    """
    Create a new voice/chat session for the user.
    Applies tier-based access control rules and returns a session ID.
    """
    user_id, tier = user_info
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    logger.info(
        f"Session create request from {user_id} ({tier}) | IP: {client_ip} | UA: {user_agent}"
    )

    try:
        # Check tier & usage permissions
        check = await access_control.check_permission(user_id, tier)
        if not check.allowed:
            raise HTTPException(
                status_code=403, detail={"reason": check.reason, "action": check.action}
            )

        # Generate unique session ID
        session_id = str(uuid4())

        # Track session in Redis
        await access_control.start_session(user_id, session_id)
        
        voice = get_voice_by_id(body.voice_id).model_dump()   
        agent_config = json.dumps({
            "model_id": body.model_id,
            "voice": voice
        })
        
        # Create LiveKit room
        await livekit_service.create_room(session_id, agent_config)
        
       # Save to Redis for the worker to fetch later
        await redis_client.setex(
            f"Agent Config:{session_id}",
            1800,  # expire in 30 mins  TODO match session length
            json.dumps(agent_config)
        )

        # Generate LiveKit token
        livekit_token = livekit_service.generate_token(
            session_id,
            user_id,
        )

        return {
            "session_id": session_id,
            "tier": tier,
            "livekit_url": livekit_service.livekit_url,
            "livekit_token": livekit_token,
            "ip": client_ip,
            "user_agent": user_agent,
        }

    except TierNotFoundError as e:
        logger.warning(f"Tier not found for user {user_id}: {e}")
        raise HTTPException(
            status_code=400, detail={"reason": e.reason, "action": e.action}
        )

    except LimitExceededError as e:
        logger.info(f"Limit exceeded for user {user_id}: {e}")
        raise HTTPException(
            status_code=403, detail={"reason": e.reason, "action": e.action}
        )

    except Exception as e:
        logger.exception(f"Unexpected error creating session for {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{session_id}", status_code=status.HTTP_202_ACCEPTED)
async def end_session(
    session_id: str,
    body: EndSessionRequest,
    request: Request,
    user_info=Depends(get_user_id_or_guest),
):
    """
    End an active session and record its duration in usage limits.
    """
    user_id, tier = user_info
    client_ip = request.client.host

    try:
        # Validate that the session exists for the user
        active_sessions = await access_control.get_active_sessions(user_id)
        if active_sessions == 0:
            raise HTTPException(status_code=404, detail="No active sessions found")

        duration_seconds = body.duration_seconds
        if duration_seconds <= 0:
            logger.warning(f"No valid session duration provided for {session_id}")
            duration_seconds = 0

        # Remove session from Redis & update daily usage
        await access_control.end_session(user_id, session_id, duration_seconds)

        # Delete LiveKit room
        await livekit_service.delete_room(session_id)

        logger.info(
            f"Ended session {session_id} for {user_id} | "
            f"Duration: {duration_seconds}s | IP: {client_ip}"
        )

        return {
            "status": "ended",
            "session_id": session_id,
            "duration_seconds": duration_seconds,
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Error ending session {session_id} for {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
