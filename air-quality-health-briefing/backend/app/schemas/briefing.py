from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BriefingGenerateRequest(BaseModel):
    location_id: Optional[str] = None


class BriefingResponse(BaseModel):
    id: str
    user_id: str
    location_id: Optional[str] = None
    aqi_at_generation: Optional[int] = None
    outdoor_safety: Optional[str] = None
    summary: str
    mask_recommendation: Optional[str] = None
    symptom_watch: list[str] = []
    best_time_window: Optional[str] = None
    activity_guidance: str
    historical_context: Optional[str] = None
    is_cached_result: bool
    generated_at: datetime

    class Config:
        from_attributes = True


class QuotaStatusResponse(BaseModel):
    daily_limit: int
    remaining: int
    resets_at: str = "00:00 UTC"
