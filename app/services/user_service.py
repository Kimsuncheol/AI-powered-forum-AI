"""User business logic service."""

from app.core.exceptions import NotFoundError


async def get_user(user_id: str) -> dict:
    """Get user profile by ID."""
    # TODO: Implement database query
    raise NotFoundError(f"User {user_id} not found")


async def get_user_by_email(email: str) -> dict | None:
    """Get user by email address."""
    # TODO: Implement database query
    return None


async def create_user_profile(user_id: str, email: str, display_name: str) -> dict:
    """Create or update user profile from Firebase data."""
    # TODO: Implement database upsert
    return {
        "id": user_id,
        "email": email,
        "display_name": display_name,
    }
