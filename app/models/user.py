from datetime import datetime
from sqlmodel import SQLModel, Field, text, UUID as SQLModelUUID, Column, JSON, Relationship, DateTime
from pydantic import EmailStr
from uuid import UUID
from typing import List, Optional
from app.utils.datetime_now import datetime_now
from sqlalchemy.dialects.postgresql import ENUM
from app.permissions import RoleType, PermissionsType

user_role_enum = ENUM(
    "customer", "support_staff", "store_manager", "super_admin",
    name="user_role",
)

class TokenData(SQLModel):
    """JWT token payload structure"""
    sub: str
    permissions: List[PermissionsType] = []
    roles: List[RoleType] = []
    exp: datetime

class RoleHierarchy(SQLModel, table=True):
    parent_role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    child_role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime_now)

class UserRole(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: UUID = Field(foreign_key="role.id", primary_key=True)

class RolePermission(SQLModel, table=True):
    role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permission.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole, sa_relationship_kwargs={
            "cascade": "save-update, merge",
            "passive_deletes": False
        })

    # Security metadata
    last_login: Optional[datetime] = Field(default=None)
    failed_login_attempts: int = Field(default=0)
    mfa_enabled: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime_now(),
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"))
    )
    updated_at: Optional[datetime] = Field(default=None)

class Role(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    name: RoleType = Field(
        sa_column=Column(
            user_role_enum,
            unique=True,
            nullable=False,
            index=True
        )
    )
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission, sa_relationship_kwargs={
            "cascade": "save-update, merge",
            "passive_deletes": False
        })
    users: List[User] = Relationship(back_populates="roles", link_model=UserRole)
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: Optional[datetime] = Field(default=None)

class Permission(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    name: PermissionsType = Field(unique=True, index=True)
    description: str = Field(max_length=200)
    roles: List[Role] = Relationship(back_populates="permissions", link_model=RolePermission, sa_relationship_kwargs={
            "cascade": "save-update, merge",
            "passive_deletes": False
        })
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: Optional[datetime] = Field(default=None)

class PermissionAuditLog(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    user_id: UUID = Field(foreign_key="user.id")
    action: str  # 'grant' or 'revoke'
    role_id: UUID = Field(foreign_key="role.id")
    permission_id: UUID = Field(foreign_key="permission.id")
    timestamp: datetime = Field(default_factory=datetime_now)
    reason: Optional[str]