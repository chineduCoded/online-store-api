from datetime import datetime, timedelta, timezone
from typing import List, Optional, Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import get_settings
from app.db import get_session
from app.models.user import User, TokenData, Role, UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
from app.permissions import PermissionsType, RoleType
from sqlmodel import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

settings = get_settings()

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short expiration for security
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Long expiration for convenience
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Generate a JWT refresh token"""
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the database using the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        token_data = TokenData(
            sub=payload.get("sub"),
            permissions=payload.get("permissions", []),
            roles=payload.get("roles", []),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
        
        if not token_data.sub:
            raise credentials_exception

        result = await session.exec(select(User).where(User.email == token_data.sub))
        user = result.first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
async def refresh_access_token(refresh_token: str, session: AsyncSession = Depends(get_session)) -> str:
    """Generate a new access token using a valid refresh token."""
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[ALGORITHM])
        email = payload.get("sub")

        user = await session.get(User, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_access_token = create_access_token({"sub": email, "roles": [role.name for role in user.roles]})
        return new_access_token
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
class RoleManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def assign_role(self, user_id: UUID, role_type: RoleType) -> None:
        """Assign a role to a user"""
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        result = await self.session.exec(select(Role).where(Role.name == role_type))
        role = result.first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.session.add(user_role)
        await self.session.commit()

    async def remove_role(self, user_id: UUID, role_type: RoleType) -> None:
        """Remove a role from a user"""
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        result = await self.session.exec(select(Role).where(Role.name == role_type))
        role = result.first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        user_role = await self.session.get(UserRole, (user_id, role.id))
        if not user_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not assigned to user")

        self.session.delete(user_role)
        await self.session.commit()
    
class PermissionChecker:
    """Utility class to check if a user has a permission"""
    def __init__(self, required_permissions: List[PermissionsType], require_all: bool = False):
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        # Collect permissions from all roles
        user_permissions = set()
        for role in user.roles:
            user_permissions.update(permission.name for permission in role.permissions)

        if self.require_all:
            has_permissions = all(permission in user_permissions for permission in self.required_permissions)
        else:
            has_permissions = any(permission in user_permissions for permission in self.required_permissions)

        # Check if user has required permissions
        if not has_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation"
            )
        return user
