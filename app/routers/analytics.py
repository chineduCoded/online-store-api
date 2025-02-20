from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User, Role
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session
from app.security.auth import get_current_user
from app.permissions import PermissionsType

router = APIRouter()

async def vaidate_analytics_access(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Check if the user has permission to access analytics"""
    result = await session.exec(select(Role).where(Role.name == PermissionsType.ANALYTICS_VIEW))
    analytics_permisssion = result.first()

    has_permission: False
    for role in user.roles:
        if analytics_permisssion in role.permissions:
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to analytics")
    
    return user

@router.get("/analytics", summary="Get analytics data", dependencies=[Depends(vaidate_analytics_access)])
async def get_analytics_data():
    return {"data": "analytics data"}