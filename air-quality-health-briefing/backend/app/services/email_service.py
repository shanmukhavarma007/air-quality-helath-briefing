import httpx
from loguru import logger
from app.config import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class EmailService:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_briefing_email(
        self, to_email: str, to_name: str, briefing: dict, aqi_value: int, location_label: str
    ) -> bool:
        html_content = f"""
        <h2>Good morning, {to_name}</h2>
        <p><strong>Location:</strong> {location_label} | <strong>AQI:</strong> {aqi_value}</p>
        <hr>
        <p>{briefing['summary']}</p>
        <p><strong>Outdoor Safety:</strong> {briefing['outdoor_safety'].upper()}</p>
        <p><strong>Activity Guidance:</strong> {briefing['activity_guidance']}</p>
        {"<p><strong>Mask:</strong> " + briefing['mask_recommendation'] + "</p>" if briefing.get('mask_recommendation') else ""}
        {"<p><strong>Best Window:</strong> " + briefing['best_time_window'] + "</p>" if briefing.get('best_time_window') else ""}
        <hr>
        <p style="font-size:12px;color:#888;">
            <a href="{{unsubscribe}}">Unsubscribe</a>
        </p>
        """
        payload = {
            "sender": {"name": settings.FROM_NAME, "email": settings.FROM_EMAIL},
            "to": [{"email": to_email, "name": to_name}],
            "subject": f"Air Quality Brief — {location_label} | AQI {aqi_value}",
            "htmlContent": html_content,
        }
        try:
            response = await self.client.post(BREVO_API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Briefing email sent to {to_email}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo email failed for {to_email}: {e.response.text}")
            return False

    async def send_verification_email(self, to_email: str, to_name: str, token: str) -> bool:
        verify_url = f"{settings.APP_URL}/verify-email?token={token}"
        payload = {
            "sender": {"name": settings.FROM_NAME, "email": settings.FROM_EMAIL},
            "to": [{"email": to_email, "name": to_name}],
            "subject": "Verify your AirBrief account",
            "htmlContent": f"<p>Click to verify: <a href='{verify_url}'>{verify_url}</a></p><p>Expires in 24 hours.</p>",
        }
        try:
            response = await self.client.post(BREVO_API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Verification email failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()
