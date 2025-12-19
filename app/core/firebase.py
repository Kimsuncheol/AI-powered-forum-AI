"""Firebase authentication module."""

import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials, initialize_app

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
        if not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            logger.warning(
                f"Firebase credentials not found at {settings.FIREBASE_CREDENTIALS_PATH}. "
                "Auth will fail unless using mocks."
            )
            # We don't raise here so the app can start, but verify_id_token will fail
            return

        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # In production, we might want to raise this
        # raise


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

        # If we are in dev mode and credentials path is special, we could mock
        # For now, we try real verification
        decoded_token = auth.verify_id_token(token)
        return decoded_token

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
