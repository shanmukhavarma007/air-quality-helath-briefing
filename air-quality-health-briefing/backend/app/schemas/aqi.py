from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AQICurrentResponse(BaseModel):
    aqi_value: int
    category: str
    hex_color: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    o3: Optional[float] = None
    no2: Optional[float] = None
    co: Optional[float] = None
    so2: Optional[float] = None
    station_name: str
    station_distance: Optional[float] = None
    last_updated: datetime


class AQIHourlyResponse(BaseModel):
    hourly: list[dict]
    best_window: Optional[str] = None
    worst_window: Optional[str] = None


class AQILocation(BaseModel):
    id: int
    name: str
    distance: float
    latitude: float
    longitude: float
