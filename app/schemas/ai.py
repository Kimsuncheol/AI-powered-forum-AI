"""AI-related Pydantic schemas."""

from enum import Enum

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Request schema for thread summarization."""

    content: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Thread content to summarize",
        examples=["This is a long discussion about AI and machine learning..."],
    )


class SummarizeResponse(BaseModel):
    """Response schema for thread summarization."""

    summary: str = Field(
        ...,
        description="AI-generated summary of the thread content",
        examples=["This thread discusses the applications of AI in modern software development."],
    )


class QARequest(BaseModel):
    """Request schema for Q&A."""

    context: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Context to answer from",
        examples=["The discussion covered various deployment strategies including blue-green..."],
    )
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Question to answer",
        examples=["What deployment strategy was recommended?"],
    )


class QAResponse(BaseModel):
    """Response schema for Q&A."""

    answer: str = Field(
        ...,
        description="AI-generated answer based on the provided context",
        examples=["Based on the discussion, blue-green deployment was recommended for zero-downtime releases."],
    )


class RewriteMode(str, Enum):
    """Supported text rewrite modes."""

    CLARITY = "clarity"
    SHORTEN = "shorten"
    POLITE = "polite"
    TRANSLATE = "translate"


class RewriteRequest(BaseModel):
    """Request schema for text rewriting."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to rewrite",
        examples=["This code is really bad and needs to be fixed ASAP."],
    )
    mode: RewriteMode = Field(
        ...,
        description="Rewriting mode to apply",
        examples=["polite"],
    )
    target_language: str | None = Field(
        default="Korean",
        description="Target language for translation mode (ignored for other modes)",
        examples=["Korean", "Japanese", "Spanish"],
    )


class RewriteResponse(BaseModel):
    """Response schema for text rewriting."""

    rewritten_text: str = Field(
        ...,
        description="AI-rewritten text according to the specified mode",
        examples=["I noticed some areas in this code that could benefit from improvement. Would it be possible to address these at your earliest convenience?"],
    )
    mode: RewriteMode = Field(
        ...,
        description="The mode that was applied",
    )


class ModerationRequest(BaseModel):
    """Request schema for content moderation."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Content to moderate",
        examples=["This forum has great discussions about technology!"],
    )


class ModerationResponse(BaseModel):
    """Response schema for content moderation."""

    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Risk score from 0.0 (safe) to 1.0 (high risk)",
        examples=[0.15],
    )
    reason_tags: list[str] = Field(
        ...,
        description="List of concern categories (spam, harassment, hate_speech, explicit, violence, misinformation, off_topic)",
        examples=[[]],
    )
    explanation: str = Field(
        ...,
        description="Brief explanation of the moderation assessment",
        examples=["Content appears to be appropriate discussion about technology."],
    )
    flagged_for_review: bool = Field(
        ...,
        description="Whether content should be flagged for human review (risk_score >= 0.5)",
    )
