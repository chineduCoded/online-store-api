from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID
from typing import List
from app.security.auth import PermissionChecker, create_access_token, create_refresh_token, refresh_access_token, RoleManager
from app.security.hashing import verify_password, get_password_hash
from app.models.user import User, Role
from app.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate, LoginAccessTokenRead
from sqlalchemy.exc import IntegrityError
from app.permissions import PermissionsType, RoleType

router = APIRouter()

@router.post("/token", summary="Get a token", response_model=LoginAccessTokenRead)
async def login_for_access_token(session: AsyncSession = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return an access token and refresh token"""
    result = await session.exec(select(User).where(User.email == form_data.username))
    user = result.first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email, "roles": [role.name for role in user.roles]})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token/refresh", summary="Refresh a token")
async def refresh_token(refresh_token: str):
    """Refresh an expired access token using a valid refresh token"""
    new_access_token = refresh_access_token(refresh_token)
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a new user"""
    user_data = user_in.model_dump()
    user_data["hashed_password"] = get_password_hash(user_in.password)

    user_data.pop("password", None)

    user = User.model_validate(user_data)

    default_role = await session.exec(select(Role).where(Role.name == RoleType.CUSTOMER))
    role = default_role.first()

    user.roles = [role] if role else []
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)

        result = await session.exec(select(User).where(User.id == user.id).options(selectinload(User.roles)))
        user = result.first()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return user

@router.get("/users", response_model=list[UserRead], summary="Get all users", dependencies=[Depends(PermissionChecker([PermissionsType.USER_READ]))])
async def read_users(session: AsyncSession = Depends(get_session)):
    users = await session.exec(select(User))
    return users.all()

@router.get("/users/{user_id}", response_model=UserRead, summary="Get a user by ID", dependencies=[Depends(PermissionChecker([PermissionsType.USER_READ]))])
async def read_user(user_id: str, session: AsyncSession = Depends(get_session)):
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/users/me", response_model=UserRead, summary="Get the current user")
async def read_current_user(user: User = Depends(get_session)):
    return user

@router.patch("/users/{user_id}", response_model=UserRead, summary="Update a user by ID", dependencies=[Depends(PermissionChecker([PermissionsType.USER_MANAGE]))])
async def update_user(user_id: str, user_in: UserUpdate, session: AsyncSession = Depends(get_session)):
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    await session.commit()
    await session.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user by ID", dependencies=[Depends(PermissionChecker([PermissionsType.USER_MANAGE]))])
async def delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    session.delete(user)
    await session.commit()
    return

@router.post("/users/{user_id}/permissions", dependencies=[Depends(PermissionChecker([PermissionsType.USER_MANAGE]))])
async def grant_permission(user_id: str, permission: str, session: AsyncSession = Depends(get_session)):
    """Grant a permission to a user"""
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if permission not in user.permissions:
        user.permissions.append(permission)
    
    session.add(user)
    await session.commit()
    return {"message": f"Permission '{permission}' granted to {user.email}"}

@router.post("/users/{user_id}/roles", dependencies=[Depends(PermissionChecker([PermissionsType.USER_MANAGE_ROLES]))])
async def manage_user_roles(user_id: str, role: List[RoleType], session: AsyncSession = Depends(get_session)):
    """Assign a role to a user"""
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    role_manager = RoleManager(session)
    for role_type in role:
        await role_manager.assign_role(user_id, role_type)

    return {"message": f"Roles '{role}' assigned to user"}