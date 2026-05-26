from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserRegister, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictError, UnauthorizedError, BadRequestError
from app.redis_client import get_redis


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Email or username already taken")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is inactive")

    return TokenResponse(
        access_token=create_access_token(str(user.id), {"role": user.role}),
        refresh_token=create_refresh_token(str(user.id)),
    )


async def refresh_tokens(refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except (ValueError, KeyError):
        raise UnauthorizedError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise BadRequestError("Not a refresh token")

    user_id = payload["sub"]
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


async def logout_user(token: str):
    try:
        payload = decode_token(token)
        jti = payload.get("jti", "")
        import math
        from datetime import datetime, timezone
        exp = payload.get("exp", 0)
        ttl = max(1, math.ceil(exp - datetime.now(timezone.utc).timestamp()))
        redis = await get_redis()
        await redis.setex(f"token:denylist:{jti}", ttl, "1")
    except (ValueError, KeyError):
        pass  # already invalid, no action needed
