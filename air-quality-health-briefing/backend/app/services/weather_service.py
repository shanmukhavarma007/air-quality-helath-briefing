import httpx
from loguru import logger
from app.services.cache_service import CacheService

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"


class WeatherService:
    def __init__(self, cache: CacheService):
        self.cache = cache
        self.client = httpx.AsyncClient(base_url=OPEN_METEO_BASE_URL, timeout=10.0)

    async def get_current_weather(self, lat: float, lon: float) -> dict:
        cache_key = f"weather:current:{lat:.4f}:{lon:.4f}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        response = await self.client.get(
            "/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "forecast_days": 1,
                "timezone": "auto",
            }
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=1800)
        return data

    async def close(self):
        await self.client.aclose()
