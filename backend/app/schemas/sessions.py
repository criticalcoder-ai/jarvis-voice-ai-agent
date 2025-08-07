from typing import Optional
from pydantic import BaseModel
from pydantic import Field

DEFAULT_MODEL_ID = "google/gemini-2.5-flash-lite"
DEFAULT_VOICE_ID = "default-voice" # TODO: Replace with actual voice ID

class CreateSessionRequest(BaseModel):
    model_id: Optional[str] = Field(DEFAULT_MODEL_ID, description="AI model identifier to use for the session")
    voice_id: Optional[str] = Field(DEFAULT_VOICE_ID, description="Voice identifier to use for speech synthesis")

class EndSessionRequest(BaseModel):
    duration_seconds: int = Field(..., description="Duration of the session in seconds")