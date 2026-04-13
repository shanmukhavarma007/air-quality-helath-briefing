from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class HealthProfileUpdate(BaseModel):
    age_bracket: Optional[str] = None
    conditions: Optional[list[str]] = None
    activity_level: Optional[str] = None
    briefing_time: Optional[str] = None
    timezone: Optional[str] = None


class HealthProfileResponse(BaseModel):
    id: str
    user_id: str
    age_bracket: str
    conditions: list[str]
    activity_level: str
    briefing_time: str
    timezone: str

    class Config:
        from_attributes = True


class LocationCreate(BaseModel):
    label: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    is_primary: bool = False
    alert_threshold: int = 150


class LocationResponse(BaseModel):
    id: str
    user_id: str
    label: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    is_primary: bool
    alert_threshold: int

    class Config:
        from_attributes = True
