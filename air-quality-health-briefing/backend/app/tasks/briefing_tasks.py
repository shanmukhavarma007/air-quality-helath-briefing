from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, UserLocation, HealthProfile, Briefing
from app.services.cache_service import CacheService
from app.services.openaq_service import OpenAQService
from app.services.weather_service import WeatherService
from app.services.ai_service import AIService, QuotaExhaustedException
from app.services.aqi_calculator import get_aqi_category, PM25_BREAKPOINTS, calculate_aqi
from app.services.email_service import EmailService
from app.services.ntfy_service import NtfyService
from app.services.pdf_report_service import PDFReportService
from loguru import logger
import redis.asyncio as aioredis
from app.config import settings


@shared_task
def generate_daily_briefing(user_id: str, location_id: str):
    import asyncio
    asyncio.run(_generate_daily_briefing_async(user_id, location_id))


async def _generate_daily_briefing_async(user_id: str, location_id: str):
    async with async_session_maker() as db:
        cache_service = CacheService()
        weather_service = WeatherService(cache_service)
        openaq_service = OpenAQService(cache_service)
        redis_client = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        ai_service = AIService(cache_service, redis_client)
        
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User {user_id} not found")
                return
            
            result = await db.execute(select(UserLocation).where(UserLocation.id == location_id))
            location = result.scalar_one_or_none()
            if not location:
                logger.warning(f"Location {location_id} not found")
                return
            
            result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == user_id))
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
            
            weather_data = await weather_service.get_current_weather(float(location.latitude), float(location.longitude))
            aqi_data_raw = await openaq_service.get_latest_by_location(float(location.latitude), float(location.longitude))
            
            pm25_value = None
            if aqi_data_raw.get("results"):
                for m in aqi_data_raw["results"][0].get("measurements", []):
                    if m.get("parameter") == "pm25":
                        pm25_value = m.get("value")
                        break
            
            aqi_value = calculate_aqi(pm25_value or 0, PM25_BREAKPOINTS) if pm25_value else 0
            category, hex_color = get_aqi_category(aqi_value)
            
            aqi_data = {"aqi_value": aqi_value, "category": category, "pm25": pm25_value}
            
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
            
            briefing = Briefing(
                user_id=user.id,
                location_id=location.id,
                aqi_at_generation=aqi_value,
                outdoor_safety=briefing_content.get("outdoor_safety"),
                brief_text=briefing_content.get("summary", ""),
                brief_metadata=briefing_content,
                model_used=model_used,
                is_cached_result=is_cached,
                delivered_email=True
            )
            db.add(briefing)
            await db.commit()
            
            email_service = EmailService()
            ntfy_service = NtfyService()
            
            # Send email briefing
            await email_service.send_briefing_email(
                user.email,
                user.full_name or "User",
                briefing_content,
                aqi_value,
                location.label
            )
            
            # Send push notification if AQI is above threshold
            if aqi_value >= location.alert_threshold:
                await ntfy_service.send_aqi_alert(
                    user_email=user.email,
                    user_name=user.full_name or "User",
                    aqi_value=aqi_value,
                    category=briefing_content.get("outdoor_safety", "Unknown"),
                    location_label=location.label,
                    threshold=location.alert_threshold
                )
            
            await email_service.close()
            await ntfy_service.close()
            
            logger.info(f"Daily briefing generated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generating daily briefing: {e}")
        finally:
            await weather_service.close()
            await openaq_service.close()
            await ai_service.close()
            await redis_client.close()


@shared_task
def refresh_aqi_data(lat: float, lon: float):
    import asyncio
    asyncio.run(_refresh_aqi_data_async(lat, lon))


async def _refresh_aqi_data_async(lat: float, lon: float):
    cache_service = CacheService()
    openaq_service = OpenAQService(cache_service)
    
    try:
        await openaq_service.get_latest_by_location(lat, lon)
        logger.info(f"AQI data refreshed for {lat}, {lon}")
    finally:
        await openaq_service.close()
