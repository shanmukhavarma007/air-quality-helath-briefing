from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, HealthProfile
from app.schemas.user import UserResponse, HealthProfileUpdate, HealthProfileResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/profile", response_model=HealthProfileResponse)
async def get_health_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.put("/profile", response_model=HealthProfileResponse)
async def update_health_profile(
    request: HealthProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)

    if request.age_bracket is not None:
        profile.age_bracket = request.age_bracket
    if request.conditions is not None:
        profile.conditions = request.conditions
    if request.activity_level is not None:
        profile.activity_level = request.activity_level
    if request.briefing_time is not None:
        profile.briefing_time = request.briefing_time
    if request.timezone is not None:
        profile.timezone = request.timezone

    await db.commit()
    await db.refresh(profile)
    return profile
