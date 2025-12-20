"""Image generation related Pydantic schemas."""

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Request schema for generating an image from a text prompt."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt to generate image from",
        examples=["A futuristic city with flying cars"],
    )


class ImageResponse(BaseModel):
    """Response schema for image generation/editing."""

    url: str | None = Field(
        None,
        description="URL of the generated image (if hosted)",
    )
    b64_json: str | None = Field(
        None,
        description="Base64 encoded image data (if returned directly)",
    )
    revised_prompt: str | None = Field(
        None,
        description="The actual prompt used by the model (if revised)",
    )
