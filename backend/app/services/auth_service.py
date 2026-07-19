"""
CrimeLens AI — Authentication Service
========================================
Business logic for user registration, login, and token management.
Sits between the router layer and the user repository.
"""

from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.middleware.auth import hash_password, verify_password, create_access_token
from app.repositories.user_repository import user_repository
from app.models.user import UserCreate, UserLogin, UserInDB


class AuthService:
    """Handles registration, authentication, and token issuance."""

    def __init__(self):
        self.repo = user_repository

    async def register(self, data: UserCreate) -> dict:
        """
        Register a new user.
        - Checks for duplicate email
        - Hashes password with bcrypt
        - Creates user document in MongoDB
        - Returns JWT token response
        """
        # Check if email already exists
        existing = await self.repo.find_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        # Build user document
        user_doc = UserInDB(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        ).model_dump()

        # Insert into MongoDB
        user_id = await self.repo.create_user(user_doc)

        # Generate JWT
        token, expiry = create_access_token(
            user_id=user_id,
            email=data.email,
            role=data.role.value,
        )

        # Build response
        user_response = await self.repo.find_by_id(user_id)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expiry,
            "user": user_response,
        }

    async def login(self, data: UserLogin) -> dict:
        """
        Authenticate user with email and password.
        - Validates credentials
        - Updates last_login timestamp
        - Returns JWT token response
        """
        # Find user by email
        user = await self.repo.find_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Verify password
        if not verify_password(data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Check if account is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Contact an administrator.",
            )

        # Update last login time
        now = datetime.now(timezone.utc)
        await self.repo.update_last_login(user["_id"], now)

        # Generate JWT
        token, expiry = create_access_token(
            user_id=user["_id"],
            email=user["email"],
            role=user["role"],
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expiry,
            "user": {
                "_id": user["_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user.get("is_active", True),
                "created_at": user["created_at"],
                "last_login": now.isoformat(),
            },
        }

    async def get_profile(self, user_id: str) -> dict:
        """Get the current user's profile by their ID."""
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        # Never return password hash
        user.pop("password_hash", None)
        return user


# Singleton instance
auth_service = AuthService()
