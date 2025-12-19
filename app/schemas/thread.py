"""Thread-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ThreadBase(BaseModel):
    """Base thread schema."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class ThreadCreate(ThreadBase):
    """Schema for creating a thread."""

    pass


class ThreadUpdate(BaseModel):
    """Schema for updating a thread (partial update)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)


class ThreadResponse(ThreadBase):
    """Schema for thread response."""

    id: str
    author_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
