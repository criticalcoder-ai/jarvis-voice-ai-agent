from pydantic import BaseModel
from pydantic import Field

class EndSessionRequest(BaseModel):
    duration_seconds: int = Field(..., description="Duration of the session in seconds")