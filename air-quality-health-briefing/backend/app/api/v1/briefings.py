from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserLocation, HealthProfile, Briefing
from app.schemas.briefing import BriefingGenerateRequest, BriefingResponse, QuotaStatusResponse
from app.services.cache_service import CacheService
from app.services.openaq_service import OpenAQService
from app.services.weather_service import WeatherService
from app.services.ai_service import AIService, QuotaExhaustedException
from app.services.aqi_calculator import get_aqi_category, PM25_BREAKPOINTS, calculate_aqi
from app.api.v1.auth import get_current_user
import redis.asyncio as aioredis
from app.core.rate_limiter import get_ai_quota_remaining
from app.config import settings
from datetime import datetime
from loguru import logger

router = APIRouter(prefix="/briefings", tags=["briefings"])
cache_service = CacheService()


async def get_redis():
    return aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


@router.post("/generate", response_model=BriefingResponse)
async def generate_briefing(
    request: BriefingGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    redis_client = await get_redis()
    weather_service = WeatherService(cache_service)
    openaq_service = OpenAQService(cache_service)
    ai_service = AIService(cache_service, redis_client)
    
    try:
        location = None
        if request.location_id:
            result = await db.execute(
                select(UserLocation).where(
                    UserLocation.id == request.location_id,
                    UserLocation.user_id == current_user.id
                )
            )
            location = result.scalar_one_or_none()
        
        if not location:
            result = await db.execute(
                select(UserLocation).where(
                    UserLocation.user_id == current_user.id,
                    UserLocation.is_primary == True
                )
            )
            location = result.scalar_one_or_none()
        
        if not location:
            result = await db.execute(
                select(UserLocation).where(UserLocation.user_id == current_user.id)
            )
            location = result.scalars().first()
        
        if not location:
            raise HTTPException(status_code=400, detail="No location found. Please add a location first.")
        
        result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
        health_profile = result.scalar_one_or_none()
        
        if not health_profile:
            health_profile = {
                "age_bracket": "adult",
                "conditions": [],
                "activity_level": "moderate"
            }
        else:
            health_profile = {
                "age_bracket": health_profile.age_bracket,
                "conditions": health_profile.conditions or [],
                "activity_level": health_profile.activity_level
            }
        
        weather_data = await weather_service.get_current_weather(location.latitude, location.longitude)
        aqi_data_raw = await openaq_service.get_latest_by_location(location.latitude, location.longitude)
        
        pm25_value = None
        if aqi_data_raw.get("results"):
            for m in aqi_data_raw["results"][0].get("measurements", []):
                if m.get("parameter") == "pm25":
                    pm25_value = m.get("value")
                    break
        
        aqi_value = calculate_aqi(pm25_value or 0, PM25_BREAKPOINTS) if pm25_value else 0
        category, hex_color = get_aqi_category(aqi_value)
        
        aqi_data = {
            "aqi_value": aqi_value,
            "category": category,
            "pm25": pm25_value
        }
        
        weather_info = {
            "temp": weather_data.get("current", {}).get("temperature_2m"),
            "humidity": weather_data.get("current", {}).get("relative_humidity_2m"),
            "wind_speed": weather_data.get("current", {}).get("wind_speed_10m")
        }
        
        try:
            briefing_content = await ai_service.generate_health_briefing(aqi_data, weather_info, health_profile)
            is_cached = False
            model_used = "google/gemma-3-27b-it:free"
        except QuotaExhaustedException:
            cache_key = f"briefing:fallback:{aqi_value}"
            cached = await cache_service.get(cache_key)
            if cached:
                briefing_content = cached
                is_cached = True
                model_used = "cached"
            else:
                briefing_content = {
                    "summary": "AI quota exhausted. Please try again tomorrow.",
                    "outdoor_safety": "caution",
                    "mask_recommendation": None,
                    "symptom_watch": [],
                    "best_time_window": None,
                    "activity_guidance": "Check local air quality reports for updates.",
                    "historical_context": "Unable to generate historical context due to AI quota limits."
                }
                is_cached = True
                model_used = "fallback"
        except Exception as e:
            logger.error(f"Briefing generation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate briefing")
        
        briefing = Briefing(
            user_id=current_user.id,
            location_id=location.id,
            aqi_at_generation=aqi_value,
            outdoor_safety=briefing_content.get("outdoor_safety"),
            brief_text=briefing_content.get("summary", ""),
            brief_metadata=briefing_content,
            model_used=model_used,
            is_cached_result=is_cached
        )
        db.add(briefing)
        await db.commit()
        await db.refresh(briefing)
        
        return BriefingResponse(
            id=str(briefing.id),
            user_id=str(briefing.user_id),
            location_id=str(briefing.location_id) if briefing.location_id else None,
            aqi_at_generation=briefing.aqi_at_generation,
            outdoor_safety=briefing.outdoor_safety,
            summary=briefing_content.get("summary", ""),
            mask_recommendation=briefing_content.get("mask_recommendation"),
            symptom_watch=briefing_content.get("symptom_watch", []),
            best_time_window=briefing_content.get("best_time_window"),
            activity_guidance=briefing_content.get("activity_guidance", ""),
            historical_context=briefing_content.get("historical_context"),
            is_cached_result=is_cached,
            generated_at=briefing.generated_at
        )
    finally:
        await weather_service.close()
        await openaq_service.close()
        await ai_service.close()
        await redis_client.close()


@router.get("/history", response_model=list[BriefingResponse])
async def get_briefing_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Briefing)
        .where(Briefing.user_id == current_user.id)
        .order_by(Briefing.generated_at.desc())
        .limit(limit)
    )
    briefings = result.scalars().all()
    
    return [
        BriefingResponse(
            id=str(b.id),
            user_id=str(b.user_id),
            location_id=str(b.location_id) if b.location_id else None,
            aqi_at_generation=b.aqi_at_generation,
            outdoor_safety=b.outdoor_safety,
            summary=b.brief_text,
            mask_recommendation=b.brief_metadata.get("mask_recommendation") if b.brief_metadata else None,
            symptom_watch=b.brief_metadata.get("symptom_watch", []) if b.brief_metadata else [],
            best_time_window=b.brief_metadata.get("best_time_window") if b.brief_metadata else None,
            activity_guidance=b.brief_metadata.get("activity_guidance", "") if b.brief_metadata else "",
            historical_context=b.brief_metadata.get("historical_context") if b.brief_metadata else None,
            is_cached_result=b.is_cached_result,
            generated_at=b.generated_at
        )
        for b in briefings
    ]


@router.get("/quota", response_model=QuotaStatusResponse)
async def get_quota_status(
    current_user: User = Depends(get_current_user)
):
    redis_client = await get_redis()
    try:
        remaining = await get_ai_quota_remaining(redis_client)
        return QuotaStatusResponse(daily_limit=50, remaining=remaining, resets_at="00:00 UTC")
    finally:
        await redis_client.close()
