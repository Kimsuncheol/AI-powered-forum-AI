"""Firebase authentication module."""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Firebase Admin SDK imports
# Uncomment when firebase-admin is installed:
# from firebase_admin import auth, credentials, initialize_app

from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme for bearer token
security = HTTPBearer(auto_error=False)

# Firebase initialization flag
_firebase_initialized = False


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK."""
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        # Uncomment when firebase-admin is installed:
        # cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        # initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Dependency to verify Firebase ID tokens.

    Returns:
        dict: Decoded token containing user information (uid, email, etc.)

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Initialize Firebase if not already done
        initialize_firebase()

        # Verify the token
        # Uncomment when firebase-admin is installed:
        # decoded_token = auth.verify_id_token(token)
        # return decoded_token

        # Placeholder response for development
        # Remove this when implementing actual Firebase verification
        logger.warning("Using placeholder token verification - implement Firebase!")
        return {
            "uid": "dev-user-id",
            "email": "dev@example.com",
            "email_verified": True,
        }

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Optional authentication dependency.

    Returns user info if valid token provided, None otherwise.
    Useful for endpoints that work with or without authentication.
    """
    if credentials is None:
        return None

    try:
        return await verify_firebase_token(credentials)
    except HTTPException:
        return None
