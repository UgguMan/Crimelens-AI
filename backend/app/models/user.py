"""
CrimeLens AI — User Models
============================
Pydantic schemas for user registration, authentication, and profile management.
Enforces email validation, password constraints, and role-based access levels.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.common import PyObjectId, utc_now


class UserRole(str, Enum):
    """Access control roles with increasing privilege levels."""
    VIEWER = "viewer"
    INVESTIGATOR = "investigator"
    ADMIN = "admin"


class UserCreate(BaseModel):
    """Schema for new user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = Field(default=UserRole.INVESTIGATOR)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Enforce minimum password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Strip whitespace and prevent HTML injection in names."""
        return v.strip().replace("<", "&lt;").replace(">", "&gt;")


class UserLogin(BaseModel):
    """Schema for login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Public user profile returned in API responses."""
    id: PyObjectId = Field(alias="_id")
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"populate_by_name": True}


class UserInDB(BaseModel):
    """Internal user representation stored in MongoDB."""
    email: str
    password_hash: str
    full_name: str
    role: UserRole = UserRole.INVESTIGATOR
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """JWT token response after successful authentication."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class UserUpdate(BaseModel):
    """Schema for profile updates (partial)."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
