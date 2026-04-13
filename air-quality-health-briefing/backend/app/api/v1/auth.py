from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, EmailVerification, PasswordReset
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.services.email_service import EmailService
from app.services.cache_service import CacheService
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from loguru import logger

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
cache_service = CacheService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


def generate_secure_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(request.password)
    user = User(email=request.email, password_hash=password_hash, full_name=request.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    raw_token, hashed_token = generate_secure_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    verification = EmailVerification(
        user_id=user.id,
        token=hashed_token,
        expires_at=expires
    )
    db.add(verification)
    await db.commit()

    email_service = EmailService()
    await email_service.send_verification_email(user.email, user.full_name or "User", raw_token)
    await email_service.close()

    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(request.refresh_token, refresh=True)
        email: str = payload.get("sub")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(user.email)
    new_refresh_token = create_refresh_token(user.email)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
