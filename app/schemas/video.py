"""Video generation related Pydantic schemas for Veo 3.1."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AspectRatio(str, Enum):
    """Supported video aspect ratios."""
    
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"


class Resolution(str, Enum):
    """Supported video resolutions."""
    
    HD = "720p"
    FULL_HD = "1080p"


class VideoDuration(str, Enum):
    """Supported video durations in seconds."""
    
    SHORT = "4"
    MEDIUM = "6"
    LONG = "8"


class PersonGeneration(str, Enum):
    """Person generation settings."""
    
    ALLOW_ALL = "allow_all"
    ALLOW_ADULT = "allow_adult"
    DONT_ALLOW = "dont_allow"


class VideoGenerationConfig(BaseModel):
    """Configuration for video generation."""
    
    aspect_ratio: AspectRatio = Field(
        default=AspectRatio.LANDSCAPE,
        description="Video aspect ratio (16:9 or 9:16)",
    )
    resolution: Resolution = Field(
        default=Resolution.HD,
        description="Video resolution (720p or 1080p)",
    )
    duration_seconds: VideoDuration = Field(
        default=VideoDuration.LONG,
        description="Video duration in seconds (4, 6, or 8)",
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="What to avoid in the generated video",
    )
    person_generation: PersonGeneration = Field(
        default=PersonGeneration.ALLOW_ADULT,
        description="Person generation settings",
    )
    seed: Optional[int] = Field(
        None,
        description="Seed for slightly improved determinism",
    )


class VideoGenerationRequest(BaseModel):
    """Request schema for generating a video from a text prompt."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text prompt describing the video to generate",
        examples=[
            "A cinematic shot of a majestic lion in the savannah at sunset"
        ],
    )
    config: Optional[VideoGenerationConfig] = Field(
        default_factory=VideoGenerationConfig,
        description="Video generation configuration",
    )


class VideoFromImageRequest(BaseModel):
    """Request schema for generating a video from an image."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text prompt describing animation/motion for the image",
        examples=["Panning wide shot with gentle motion"],
    )
    config: Optional[VideoGenerationConfig] = Field(
        default_factory=VideoGenerationConfig,
        description="Video generation configuration",
    )


class OperationStatus(str, Enum):
    """Status of an async video generation operation."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoGenerationResponse(BaseModel):
    """Response schema for video generation request."""
    
    operation_id: str = Field(
        ...,
        description="ID to poll for operation status",
    )
    status: OperationStatus = Field(
        default=OperationStatus.PENDING,
        description="Current status of the generation",
    )
    video_url: Optional[str] = Field(
        None,
        description="URL of the generated video (when completed)",
    )
    video_b64: Optional[str] = Field(
        None,
        description="Base64 encoded video data (when completed)",
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if generation failed",
    )


class VideoOperationStatusRequest(BaseModel):
    """Request schema for checking operation status."""
    
    operation_id: str = Field(
        ...,
        description="Operation ID returned from generate request",
    )


class VideoOperationStatusResponse(BaseModel):
    """Response schema for operation status check."""
    
    operation_id: str = Field(
        ...,
        description="The operation ID",
    )
    done: bool = Field(
        ...,
        description="Whether the operation is complete",
    )
    status: OperationStatus = Field(
        ...,
        description="Current status of the operation",
    )
    video_url: Optional[str] = Field(
        None,
        description="URL of the generated video (when completed)",
    )
    video_b64: Optional[str] = Field(
        None,
        description="Base64 encoded video data (when completed)",
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if generation failed",
    )
