from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserLocation
from app.schemas.aqi import AQICurrentResponse, AQIHourlyResponse, AQILocation
from app.services.openaq_service import OpenAQService
from app.services.weather_service import WeatherService
from app.services.cache_service import CacheService
from app.services.aqi_calculator import calculate_aqi, get_aqi_category, PM25_BREAKPOINTS, PM10_BREAKPOINTS
from app.api.v1.auth import get_current_user
from sqlalchemy import select
from loguru import logger
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/aqi", tags=["air_quality"])
cache_service = CacheService()


@router.get("/current", response_model=AQICurrentResponse)
async def get_current_aqi(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    openaq_service = OpenAQService(cache_service)
    try:
        data = await openaq_service.get_latest_by_location(lat, lon)
        
        if not data.get("results") or len(data["results"]) == 0:
            raise HTTPException(status_code=404, detail="No AQI data available for this location")

        location_data = data["results"][0]
        measurements = location_data.get("measurements", [])
        
        pm25_value = None
        pm10_value = None
        o3_value = None
        no2_value = None
        co_value = None
        so2_value = None
        
        for m in measurements:
            param = m.get("parameter")
            value = m.get("value")
            if param == "pm25":
                pm25_value = value
            elif param == "pm10":
                pm10_value = value
            elif param == "o3":
                o3_value = value
            elif param == "no2":
                no2_value = value
            elif param == "co":
                co_value = value
            elif param == "so2":
                so2_value = value

        aqi_value = None
        if pm25_value is not None:
            aqi_value = calculate_aqi(pm25_value, PM25_BREAKPOINTS)
        elif pm10_value is not None:
            aqi_value = calculate_aqi(pm10_value, PM10_BREAKPOINTS)
        
        if aqi_value is None:
            aqi_value = 0
            
        category, hex_color = get_aqi_category(aqi_value)
        
        last_updated = datetime.utcnow()
        if measurements:
            first_measurement = measurements[0]
            last_updated = datetime.fromisoformat(first_measurement.get("datetime", "").replace("Z", "+00:00"))
        
        return AQICurrentResponse(
            aqi_value=aqi_value,
            category=category,
            hex_color=hex_color,
            pm25=pm25_value,
            pm10=pm10_value,
            o3=o3_value,
            no2=no2_value,
            co=co_value,
            so2=so2_value,
            station_name=location_data.get("name", "Unknown"),
            station_distance=location_data.get("distance", None),
            last_updated=last_updated
        )
    finally:
        await openaq_service.close()


@router.get("/locations", response_model=list[AQILocation])
async def search_locations(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user)
):
    openaq_service = OpenAQService(cache_service)
    try:
        data = await openaq_service.get_latest_by_location(lat, lon)
        results = data.get("results", [])[:10]
        
        locations = []
        for loc in results:
            locations.append(AQILocation(
                id=loc.get("id"),
                name=loc.get("name", "Unknown"),
                distance=loc.get("distance", 0),
                latitude=loc.get("coordinates", {}).get("latitude", 0),
                longitude=loc.get("coordinates", {}).get("longitude", 0)
            ))
        return locations
    finally:
        await openaq_service.close()


@router.get("/history", response_model=dict)
async def get_aqi_history(
    location_id: int = Query(..., description="OpenAQ location ID"),
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user)
):
    openaq_service = OpenAQService(cache_service)
    try:
        data = await openaq_service.get_measurements(location_id, parameter="pm25", limit=24*days)
        return data
    finally:
        await openaq_service.close()
