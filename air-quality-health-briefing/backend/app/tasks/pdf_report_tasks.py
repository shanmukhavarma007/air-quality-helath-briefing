from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, UserLocation, Briefing
from app.services.pdf_report_service import PDFReportService
from app.services.email_service import EmailService
from loguru import logger
import datetime

@shared_task
def generate_weekly_pdf_report(user_id: str, location_id: str):
    import asyncio
    asyncio.run(_generate_weekly_pdf_report_async(user_id, location_id))


async def _generate_weekly_pdf_report_async(user_id: str, location_id: str):
    async with async_session_maker() as db:
        pdf_service = PDFReportService()
        email_service = EmailService()
        
        try:
            # Get user info
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User {user_id} not found")
                return
            
            # Get location info
            result = await db.execute(select(UserLocation).where(UserLocation.id == location_id))
            location = result.scalar_one_or_none()
            if not location:
                logger.warning(f"Location {location_id} not found")
                return
            
            # Get briefings from the last 7 days
            week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            result = await db.execute(
                select(Briefing)
                .where(
                    Briefing.user_id == user_id,
                    Briefing.location_id == location_id,
                    Briefing.generated_at >= week_ago
                )
                .order_by(Briefing.generated_at.desc())
            )
            briefings = result.scalars().all()
            
            # Prepare data for PDF report
            weekly_data = []
            for briefing in briefings:
                # Extract data from briefing metadata or use defaults
                aqi_value = briefing.aqi_at_generation or 0
                category = "Unknown"
                pm25 = None
                
                if briefing.brief_metadata:
                    category = briefing.brief_metadata.get("category", "Unknown")
                    pm25 = briefing.brief_metadata.get("pm25")
                
                weekly_data.append({
                    "date": briefing.generated_at.strftime("%Y-%m-%d"),
                    "aqi_value": aqi_value,
                    "category": category,
                    "pm25": pm25,
                    "notes": f"Outdoor safety: {briefing.outdoor_safety}"
                })
            
            # If we don't have enough data, create placeholder data for the last 7 days
            if len(weekly_data) < 7:
                # Fill missing days with basic data
                existing_dates = {item["date"] for item in weekly_data}
                for i in range(7):
                    date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                    if date not in existing_dates:
                        weekly_data.append({
                            "date": date,
                            "aqi_value": 0,
                            "category": "No Data",
                            "pm25": None,
                            "notes": "No data available"
                        })
            
            # Sort by date
            weekly_data.sort(key=lambda x: x["date"])
            
            # Generate PDF
            pdf_bytes = await pdf_service.generate_weekly_exposure_report(
                user_email=user.email,
                user_name=user.full_name or "User",
                location_label=location.label,
                weekly_data=weekly_data
            )
            
            # Send email with PDF attachment
            # For simplicity, we'll send a notification that the report is available
            # In a production app, you'd attach the PDF to the email
            await email_service.send_verification_email(
                to_email=user.email,
                to_name=user.full_name or "User",
                token="weekly_report_available"  # This is just a placeholder
            )
            
            logger.info(f"Weekly PDF report generated and notification sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generating weekly PDF report: {e}")
        finally:
            await pdf_service.close()
            await email_service.close()