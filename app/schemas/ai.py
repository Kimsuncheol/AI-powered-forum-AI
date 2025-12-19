"""AI-related Pydantic schemas."""

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Request schema for thread summarization."""

    content: str = Field(..., min_length=1, description="Thread content to summarize")


class SummarizeResponse(BaseModel):
    """Response schema for thread summarization."""

    summary: str


class QARequest(BaseModel):
    """Request schema for Q&A."""

    context: str = Field(..., min_length=1, description="Context to answer from")
    question: str = Field(..., min_length=1, description="Question to answer")


class QAResponse(BaseModel):
    """Response schema for Q&A."""

    answer: str
