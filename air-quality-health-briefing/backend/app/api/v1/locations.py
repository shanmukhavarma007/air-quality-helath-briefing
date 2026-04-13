from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserLocation
from app.schemas.user import LocationCreate, LocationResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationResponse])
async def get_locations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserLocation)
        .where(UserLocation.user_id == current_user.id)
        .order_by(UserLocation.sort_order, UserLocation.created_at)
    )
    locations = result.scalars().all()
    return [
        LocationResponse(
            id=str(loc.id),
            user_id=str(loc.user_id),
            label=loc.label,
            latitude=float(loc.latitude),
            longitude=float(loc.longitude),
            address=loc.address,
            is_primary=loc.is_primary,
            alert_threshold=loc.alert_threshold
        )
        for loc in locations
    ]


@router.post("", response_model=LocationResponse, status_code=201)
async def create_location(
    request: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count_result = await db.execute(
        select(UserLocation).where(UserLocation.user_id == current_user.id)
    )
    count = len(count_result.scalars().all())
    if count >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 locations allowed")
    
    if request.is_primary:
        await db.execute(
            select(UserLocation).where(
                UserLocation.user_id == current_user.id,
                UserLocation.is_primary == True
            )
        )
        result = await db.execute(
            select(UserLocation).where(
                UserLocation.user_id == current_user.id,
                UserLocation.is_primary == True
            )
        )
        primary_locs = result.scalars().all()
        for loc in primary_locs:
            loc.is_primary = False
    
    location = UserLocation(
        user_id=current_user.id,
        label=request.label,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address,
        is_primary=request.is_primary,
        alert_threshold=request.alert_threshold,
        sort_order=count
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    
    return LocationResponse(
        id=str(location.id),
        user_id=str(location.user_id),
        label=location.label,
        latitude=float(location.latitude),
        longitude=float(location.longitude),
        address=location.address,
        is_primary=location.is_primary,
        alert_threshold=location.alert_threshold
    )


@router.delete("/{location_id}")
async def delete_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserLocation).where(
            UserLocation.id == location_id,
            UserLocation.user_id == current_user.id
        )
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    await db.delete(location)
    await db.commit()
    return {"message": "Location deleted"}


@router.put("/{location_id}/primary")
async def set_primary_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserLocation).where(UserLocation.user_id == current_user.id)
    )
    locations = result.scalars().all()
    for loc in locations:
        loc.is_primary = (str(loc.id) == location_id)
    
    await db.commit()
    return {"message": "Primary location updated"}
