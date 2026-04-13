import httpx
from loguru import logger
from app.config import settings

class NtfyService:
    def __init__(self):
        self.server_url = settings.NTFY_SERVER_URL or "https://ntfy.sh"
        self.topic = settings.NTFY_TOPIC or "airqualitybriefing"
        self.headers = {
            "Content-Type": "application/json",
        }
        if settings.NTFY_USERNAME and settings.NTFY_PASSWORD:
            import base64
            credentials = base64.b64encode(
                f"{settings.NTFY_USERNAME}:{settings.NTFY_PASSWORD}".encode()
            ).decode()
            self.headers["Authorization"] = f"Basic {credentials}"
        
        self.client = httpx.AsyncClient(
            base_url=self.server_url,
            headers=self.headers,
            timeout=10.0,
        )

    async def send_notification(
        self, 
        message: str, 
        title: str = "Air Quality Alert",
        tags: str = "warning",
        priority: int = 3,
        actions: list = None
    ) -> bool:
        """
        Send a push notification via ntfy.sh
        """
        try:
            payload = {
                "topic": self.topic,
                "message": message,
                "title": title,
                "tags": tags,
                "priority": priority,
            }
            
            if actions:
                payload["actions"] = actions
                
            response = await self.client.post("", json=payload)
            response.raise_for_status()
            logger.info(f"Ntfy notification sent: {message[:50]}...")
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ntfy notification failed: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Ntfy notification error: {e}")
            return False

    async def send_aqi_alert(
        self,
        user_email: str,
        user_name: str,
        aqi_value: int,
        category: str,
        location_label: str,
        threshold: int = 150
    ) -> bool:
        """
        Send an AQI threshold alert
        """
        if aqi_value < threshold:
            return False
            
        message = f"Air quality alert for {location_label}: AQI {aqi_value} ({category})"
        title = "Air Quality Alert"
        
        actions = [
            {
                "action": "view",
                "label": "View Details",
                "url": f"{settings.APP_URL}/dashboard"
            }
        ]
        
        return await self.send_notification(
            message=message,
            title=title,
            tags="warning" if aqi_value < 200 else "exclamation",
            priority=4 if aqi_value >= 200 else 3,
            actions=actions
        )

    async def close(self):
        await self.client.aclose()