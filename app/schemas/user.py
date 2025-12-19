"""User-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    display_name: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
