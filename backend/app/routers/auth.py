from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, TokenRefresh
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(data, db)
    return TokenResponse(
        access_token=__import__("app.core.security", fromlist=["create_access_token"]).create_access_token(
            str(user.id), {"role": user.role}
        ),
        refresh_token=__import__("app.core.security", fromlist=["create_refresh_token"]).create_refresh_token(
            str(user.id)
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.login_user(data.email, data.password, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh):
    return await auth_service.refresh_tokens(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    await auth_service.logout_user(credentials.credentials)
