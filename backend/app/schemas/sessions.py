from typing import List, Literal, Optional
from uuid import UUID
from pydantic import AnyUrl, BaseModel
from pydantic import Field

DEFAULT_MODEL_ID = "google/gemini-2.5-flash"
DEFAULT_VOICE_ID = "en-US-Chirp3-HD-Charon"


class CreateSessionRequest(BaseModel):
    model_id: Optional[str] = Field(
        DEFAULT_MODEL_ID, description="AI model identifier to use for the session"
    )
    voice_id: Optional[str] = Field(
        DEFAULT_VOICE_ID, description="Voice identifier to use for speech synthesis"
    )


class EndSessionRequest(BaseModel):
    duration_seconds: int = Field(..., description="Duration of the session in seconds")


TierLiteral = Literal["guest", "free"]  # extend as you add tiers


class CreateSessionResponse(BaseModel):
    session_id: UUID = Field(..., description="Unique session identifier (UUID)")
    tier: TierLiteral = Field(..., description="The user's access tier")
    features: List[str] = Field(
        default_factory=list, description="Enabled feature flags for the tier"
    )

    # None => unlimited
    max_session_duration_seconds: Optional[int] = Field(
        None, description="Max session duration in seconds; None means unlimited"
    )
    usage_today_minutes: int = Field(
        ..., ge=0, description="Minutes used today (after this call)"
    )
    remaining_today_minutes: Optional[int] = Field(
        None, ge=0, description="Minutes remaining today; None means unlimited"
    )

    livekit_url: AnyUrl = Field(..., description="LiveKit server URL")
    livekit_token: str = Field(..., description="JWT for joining the LiveKit room")

    ip: str = Field(..., description="Client IP seen by the API")
    user_agent: str = Field(..., description="Client User-Agent header")


class EndSessionResponse(BaseModel):
    status: Literal["ended"] = Field(..., description="End-of-session marker")
    session_id: UUID = Field(..., description="The ended session id")
    duration_seconds: int = Field(
        ..., ge=0, description="Reported session duration in seconds"
    )
    usage_today_minutes: int = Field(
        ..., ge=0, description="Minutes used today (after this call)"
    )
    remaining_today_minutes: Optional[int] = Field(
        None, ge=0, description="Minutes remaining today; None means unlimited"
    )
