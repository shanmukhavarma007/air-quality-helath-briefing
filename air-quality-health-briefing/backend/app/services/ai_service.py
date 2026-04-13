import httpx
import json
from loguru import logger
from app.config import settings
from app.core.rate_limiter import check_and_increment_ai_quota
from app.services.cache_service import CacheService
import datetime

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

FREE_MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

PAID_MODELS = [
    "google/gemma-3-27b-it",
    "meta-llama/llama-3.1-8b-instruct",
    "mistralai/mistral-7b-instruct",
]

BRIEFING_SYSTEM_PROMPT = """You are a certified air quality health advisor.
Generate a concise, accurate, personalized health briefing based on current air
quality data and a user's health profile.

Rules:
- Write at a 7th-grade reading level. No jargon.
- Be specific. Avoid vague phrases like "take care".
- Base all health claims on WHO and EPA guidelines.
- Never diagnose. Recommend professional consultation for serious conditions.
- Output must be valid JSON only. No markdown, no extra text, no preamble."""


class QuotaExhaustedException(Exception):
    pass


class AIService:
    def __init__(self, cache: CacheService, redis_client):
        self.cache = cache
        self.redis = redis_client
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.APP_URL,
            "X-Title": "Air Quality Health Briefing",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=OPENROUTER_BASE_URL,
            headers=self.headers,
            timeout=30.0,
        )

    async def generate_health_briefing(
        self,
        aqi_data: dict,
        weather_data: dict,
        health_profile: dict,
    ) -> dict:

        # Try free models first with quota check
        allowed, count = await check_and_increment_ai_quota(self.redis)
        if not allowed:
            # Free quota exhausted, try paid models without quota check
            logger.info("Free AI quota exhausted, attempting paid models")
            # Reset count for paid models tracking
            count = 0

        cache_key = (
            f"briefing:cache:{aqi_data['aqi_value']}:"
            f"{'_'.join(sorted(health_profile.get('conditions', [])))}"
        )
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info("Returning cached briefing — decrementing quota back")
            await self.redis.decr(
                f"ai_quota:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}"
            )
            return cached

        user_context = f"""
Health Profile:
- Age bracket: {health_profile['age_bracket']}
- Conditions: {', '.join(health_profile.get('conditions', [])) or 'None'}
- Activity level: {health_profile['activity_level']}

Current Air Quality:
- AQI: {aqi_data['aqi_value']} ({aqi_data['category']})
- PM2.5: {aqi_data.get('pm25', 'N/A')} µg/m³
- PM10: {aqi_data.get('pm10', 'N/A')} µg/m³
- O3: {aqi_data.get('o3', 'N/A')} µg/m³

Weather:
- Temperature: {weather_data.get('temp', 'N/A')}°C
- Humidity: {weather_data.get('humidity', 'N/A')}%
- Wind: {weather_data.get('wind_speed', 'N/A')} km/h

Hourly AQI trend: {aqi_data.get('hourly_trend', [])}

Respond ONLY with JSON in exactly this format:
{{
  "summary": "2-3 sentence overall assessment",
  "outdoor_safety": "safe|caution|avoid",
  "mask_recommendation": "string or null",
  "symptom_watch": ["symptom1", "symptom2"],
  "best_time_window": "string or null",
  "activity_guidance": "1-2 sentences",
  "historical_context": "1 sentence comparing to recent days"
}}
"""

        last_error = None
        models_to_try = FREE_MODELS + PAID_MODELS
        
        for model in models_to_try:
            try:
                is_paid_model = model in PAID_MODELS
                logger.info(f"Attempting briefing with model: {model} {'(PAID)' if is_paid_model else '(FREE)'}")
                response = await self.client.post(
                    "/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": BRIEFING_SYSTEM_PROMPT},
                            {"role": "user", "content": user_context},
                        ],
                        "max_tokens": 600,
                        "temperature": 0.3,
                    }
                )
                response.raise_for_status()
                result = response.json()
                raw_text = result["choices"][0]["message"]["content"].strip()
                parsed = json.loads(raw_text)

                await self.cache.set(cache_key, parsed, ttl=7200)
                logger.info(f"Briefing generated with {model} (quota used: {count}/50)")
                return parsed

            except Exception as e:
                logger.warning(f"Model {model} failed: {e}. Trying next.")
                last_error = e
                continue

        raise RuntimeError(f"All models failed. Last error: {last_error}")

    async def close(self):
        await self.client.aclose()
