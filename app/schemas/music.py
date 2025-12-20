"""Music generation related Pydantic schemas for Lyria RealTime."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class MusicScale(str, Enum):
    """Available musical scales for Lyria."""
    
    C_MAJOR_A_MINOR = "C_MAJOR_A_MINOR"
    G_MAJOR_E_MINOR = "G_MAJOR_E_MINOR"
    D_MAJOR_B_MINOR = "D_MAJOR_B_MINOR"
    A_MAJOR_F_SHARP_MINOR = "A_MAJOR_F_SHARP_MINOR"
    E_MAJOR_C_SHARP_MINOR = "E_MAJOR_C_SHARP_MINOR"
    B_MAJOR_G_SHARP_MINOR = "B_MAJOR_G_SHARP_MINOR"
    F_MAJOR_D_MINOR = "F_MAJOR_D_MINOR"
    B_FLAT_MAJOR_G_MINOR = "B_FLAT_MAJOR_G_MINOR"
    E_FLAT_MAJOR_C_MINOR = "E_FLAT_MAJOR_C_MINOR"
    A_FLAT_MAJOR_F_MINOR = "A_FLAT_MAJOR_F_MINOR"


class MusicGenerationMode(str, Enum):
    """Music generation mode options."""
    
    QUALITY = "QUALITY"
    DIVERSITY = "DIVERSITY"
    VOCALIZATION = "VOCALIZATION"


class AudioFormat(str, Enum):
    """Supported audio output formats."""
    
    PCM16 = "pcm16"


class WeightedPrompt(BaseModel):
    """A weighted prompt for music generation."""
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Musical description (genre, instrument, mood, etc.)",
        examples=["minimal techno with deep bass"],
    )
    weight: float = Field(
        default=1.0,
        gt=0.0,
        le=5.0,
        description="Prompt weight (higher = stronger influence)",
    )


class MusicGenerationConfig(BaseModel):
    """Configuration for music generation."""
    
    bpm: int = Field(
        default=120,
        ge=60,
        le=200,
        description="Beats per minute (60-200)",
    )
    temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Generation randomness (0.0-2.0)",
    )
    guidance: float = Field(
        default=4.0,
        ge=0.0,
        le=6.0,
        description="How strictly to follow prompts (0.0-6.0)",
    )
    density: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Density of musical notes (0.0=sparse, 1.0=busy)",
    )
    brightness: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Tonal quality (0.0=dark, 1.0=bright)",
    )
    scale: Optional[MusicScale] = Field(
        None,
        description="Musical scale/key for generation",
    )
    mute_bass: bool = Field(
        default=False,
        description="Reduce bass output",
    )
    mute_drums: bool = Field(
        default=False,
        description="Reduce drums output",
    )
    only_bass_and_drums: bool = Field(
        default=False,
        description="Output only bass and drums",
    )
    music_generation_mode: MusicGenerationMode = Field(
        default=MusicGenerationMode.QUALITY,
        description="Focus on quality, diversity, or vocalization",
    )


class MusicGenerationRequest(BaseModel):
    """Request schema for generating music."""
    
    prompts: List[WeightedPrompt] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of weighted prompts describing the music",
    )
    config: Optional[MusicGenerationConfig] = Field(
        default_factory=MusicGenerationConfig,
        description="Music generation configuration",
    )
    duration_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Duration of audio to generate (5-120 seconds)",
    )
    
    @field_validator("prompts")
    @classmethod
    def validate_prompts(cls, v: List[WeightedPrompt]) -> List[WeightedPrompt]:
        """Ensure at least one prompt is provided."""
        if not v:
            raise ValueError("At least one prompt is required")
        return v


class MusicGenerationResponse(BaseModel):
    """Response schema for music generation."""
    
    audio_b64: str = Field(
        ...,
        description="Base64 encoded PCM16 audio data",
    )
    sample_rate_hz: int = Field(
        default=48000,
        description="Audio sample rate in Hz",
    )
    channels: int = Field(
        default=2,
        description="Number of audio channels (stereo=2)",
    )
    bit_depth: int = Field(
        default=16,
        description="Audio bit depth",
    )
    duration_seconds: float = Field(
        ...,
        description="Actual duration of generated audio",
    )
    prompts_used: List[str] = Field(
        default_factory=list,
        description="The prompts that were used for generation",
    )


class MusicStreamRequest(BaseModel):
    """Request schema for starting a music stream session."""
    
    prompts: List[WeightedPrompt] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Initial weighted prompts",
    )
    config: Optional[MusicGenerationConfig] = Field(
        default_factory=MusicGenerationConfig,
        description="Initial music generation configuration",
    )


class MusicStreamResponse(BaseModel):
    """Response for music stream session creation."""
    
    session_id: str = Field(
        ...,
        description="Session ID for WebSocket connection",
    )
    websocket_url: str = Field(
        ...,
        description="WebSocket URL to connect for streaming",
    )
