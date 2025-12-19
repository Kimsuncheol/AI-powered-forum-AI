"""Common API dependencies."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.firebase import verify_firebase_token
from app.services.rate_limiter import RateLimitService

# Type alias for authenticated user dependency
CurrentUser = Annotated[dict, Depends(verify_firebase_token)]


@lru_cache
def get_rate_limit_service() -> RateLimitService:
    """Get cached rate limit service instance."""
    return RateLimitService()


def check_ai_rate_limit(
    current_user: CurrentUser,
    service: RateLimitService = Depends(get_rate_limit_service),
) -> None:
    """
    Check if the user has exceeded their daily AI rate limit.
    
    Args:
        current_user: Authenticated user
        service: Rate limit service
        
    Raises:
        HTTPException: If limit exceeded (429)
    """
    user_id = current_user["uid"]
    
    if not service.check_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily AI rate limit exceeded. Please try again tomorrow.",
        )
