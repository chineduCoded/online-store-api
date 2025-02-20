from fastapi import APIRouter, Depends, HTTPException, status
from app.security.auth import RoleType
from app.security.auth import get_current_user
from app.models.user import User
from app.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

def super_Admin_only(user: User = Depends(get_current_user)):
    """Middleware to check if user is a super admin"""
    is_super_Admin = any(
        role.name == RoleType.SUPER_ADMIN for role in user.roles
    )
    if not is_super_Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return user

@router.get("/system-status", dependencies=[Depends(super_Admin_only)])
async def get_system_status(
    session: AsyncSession = Depends(get_session)
):
    """Get system status"""
    try:
        await session.exec("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}