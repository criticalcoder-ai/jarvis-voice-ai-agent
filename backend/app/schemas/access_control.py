# app/schemas/access_control.py
from pydantic import BaseModel
from typing import Optional, List

class TierLimits(BaseModel):
    name: str
    session_duration: Optional[int]  # in seconds
    concurrent_sessions: int
    daily_limit: Optional[int]       # in minutes
    features: List[str]

class AccessResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    action: Optional[str] = None
