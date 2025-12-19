"""User-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    display_name: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
