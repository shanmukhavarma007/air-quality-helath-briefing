import httpx
from loguru import logger
from app.config import settings
from app.services.cache_service import CacheService

OPENAQ_BASE_URL = "https://api.openaq.org/v3"


class OpenAQService:
    def __init__(self, cache: CacheService):
        self.cache = cache
        self.headers = {
            "X-API-Key": settings.OPENAQ_API_KEY,
            "Accept": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=OPENAQ_BASE_URL,
            headers=self.headers,
            timeout=10.0,
        )

    async def get_latest_by_location(self, lat: float, lon: float, radius: int = 10000) -> dict:
        cache_key = f"aqi:latest:{lat:.4f}:{lon:.4f}"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT for AQI at {lat},{lon}")
            return cached

        logger.info(f"Cache MISS — fetching OpenAQ data for {lat},{lon}")
        response = await self.client.get(
            "/locations",
            params={
                "coordinates": f"{lat},{lon}",
                "radius": radius,
                "limit": 5,
                "order_by": "distance",
            }
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=900)
        return data

    async def get_measurements(self, location_id: int, parameter: str = "pm25", limit: int = 24) -> dict:
        cache_key = f"aqi:measurements:{location_id}:{parameter}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        response = await self.client.get(
            f"/locations/{location_id}/measurements",
            params={"parameter": parameter, "limit": limit, "order_by": "datetime", "sort": "desc"}
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=600)
        return data

    async def close(self):
        await self.client.aclose()
