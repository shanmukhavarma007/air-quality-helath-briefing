from fastapi import APIRouter
from app.api.v1 import auth, users, air_quality, briefings, locations

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(air_quality.router)
api_router.include_router(briefings.router)
api_router.include_router(locations.router)
