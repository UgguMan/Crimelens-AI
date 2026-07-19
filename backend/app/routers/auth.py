"""
CrimeLens AI — Authentication Router
========================================
API endpoints for user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, Request

from app.models.user import UserCreate, UserLogin
from app.services.auth_service import auth_service
from app.services.log_service import log_service
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(data: UserCreate, request: Request):
    """
    Register a new user account.
    Returns JWT access token and user profile.
    """
    result = await auth_service.register(data)

    # Log the registration
    await log_service.log_action(
        user_id=result["user"]["_id"],
        action="user.registered",
        resource_type="user",
        resource_id=result["user"]["_id"],
        details={"email": data.email},
        ip_address=request.client.host if request.client else "",
    )

    return {"success": True, "data": result}


@router.post("/login")
async def login(data: UserLogin, request: Request):
    """
    Authenticate with email and password.
    Returns JWT access token and user profile.
    """
    result = await auth_service.login(data)

    # Log the login
    await log_service.log_action(
        user_id=result["user"]["_id"],
        action="user.logged_in",
        resource_type="user",
        resource_id=result["user"]["_id"],
        ip_address=request.client.host if request.client else "",
    )

    return {"success": True, "data": result}


@router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    profile = await auth_service.get_profile(current_user["user_id"])
    return {"success": True, "data": profile}
