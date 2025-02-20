from fastapi import APIRouter, Depends, HTTPException, status
from app.security.auth import RoleType
from app.security.auth import get_current_user
from app.models.user import User
from app.models.order import Order