from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.security.auth import create_access_token, create_refresh_token, refresh_access_token
from app.security.hashing import verify_password
from app.models.user import User
from app.db import get_session
from app.schemas.user_schema import LoginAccessTokenRead
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

router = APIRouter()
@router.post("/auth/token", summary="Get a token", response_model=LoginAccessTokenRead)
async def login_for_access_token(session: AsyncSession = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return an access token and refresh token"""
    result = await session.exec(select(User).where(User.email == form_data.username))
    user = result.first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email, "roles": [role.name for role in user.roles]})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/token/refresh", summary="Refresh a token")
async def refresh_token(refresh_token: str):
    """Refresh an expired access token using a valid refresh token"""
    new_access_token = refresh_access_token(refresh_token)
    return {"access_token": new_access_token, "token_type": "bearer"}