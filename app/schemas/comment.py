"""Comment-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """Base comment schema."""

    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    thread_id: str


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str = Field(..., min_length=1)


class CommentResponse(CommentBase):
    """Schema for comment response."""

    id: str
    thread_id: str
    author_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
