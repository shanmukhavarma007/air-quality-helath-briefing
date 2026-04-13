from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    level="INFO",
    colorize=True,
)

logger.add(
    "logs/app.log",
    rotation="50 MB",
    retention="10 days",
    compression="gz",
    level="WARNING",
    filter=lambda r: "api_key" not in r["message"].lower()
                     and "password" not in r["message"].lower(),
)

app = FastAPI(
    title="Air Quality Health Briefing API",
    description="AI-powered air quality health briefings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
