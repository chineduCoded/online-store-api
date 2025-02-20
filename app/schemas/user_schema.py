from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlmodel import SQLModel, Field, Column
from pydantic import ConfigDict, field_validator, EmailStr
from app.permissions import RoleType


class UserBase(SQLModel):
    email: EmailStr = Field(max_length=100)

class UserCreate(UserBase):
    password: str = Field(max_length=100)

class UserRead(SQLModel):
    id: UUID
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    roles: List[RoleType]
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    mfa_enabled: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders = {
            UUID: lambda v: str(v)
        }
    )

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    roles: Optional[List[RoleType]] = None
    
    @field_validator("roles")
    def validate_roles(cls, v):
        if v is not None and not v:
            raise ValueError("Roles cannot be empty")
        return v

    @field_validator("email")
    def validate_email(cls, v):
        if not v:
            raise ValueError("Email cannot be empty")
        return v

    @field_validator("roles")
    def validate_role(cls, v):
        if not v:
            raise ValueError("Role cannot be empty")
        return v
    
    @field_validator("password")
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        return v

class LoginAccessTokenRead(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str

