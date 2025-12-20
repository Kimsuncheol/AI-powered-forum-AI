"""Image generation endpoints using Google 'Nano Banana Pro'."""

import base64
import io
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from app.api.deps import CurrentUser
from app.schemas.image import ImageGenerationRequest, ImageResponse
from app.services.image_service import ImageService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_image_service() -> ImageService:
    """Dependency to get image service instance."""
    return ImageService()


@router.post("/generate", response_model=ImageResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: CurrentUser,
    image_service: ImageService = Depends(get_image_service),
):
    """
    Generate an image from a text prompt using Google 'Nano Banana Pro'.
    
    Args:
        request: Contains the text prompt.
        current_user: Authenticated user.
        image_service: Service to handle image generation.
        
    Returns:
        ImageResponse with base64 encoded image or URL.
    """
    try:
        logger.info(f"Image generation request from user {current_user['uid']}")
        
        # Call service to generate image
        # Returns a specialized object from the SDK, we'll need to process it.
        # For the stub implementation in service, it returns the object directly.
        # In a real integration, we'd extract bytes/url here or in service.
        result = await image_service.generate_image(request.prompt)
        
        # Assuming the service returns the PIL Image or bytes wrapper in 'result'
        # We need to convert it to base64 for the frontend if it's not a URL
        
        # If result has 'image_bytes' (common in some SDKs) or if it IS bytes/PIL
        # Let's handle generic case here assuming service might return bytes or object
        
        # Adaptation layer for the API response
        # If it's pure bytes:
        if isinstance(result, bytes):
            image_data = result
        # If it has a property like ._image_bytes or .bytes
        elif hasattr(result, "_image_bytes"):
             image_data = result._image_bytes
        elif hasattr(result, "image_bytes"):
             image_data = result.image_bytes    
        else:
             # Fallback or error if unknown structure
             # For MVP stub, lets assume it returns the bytes or something convertible
             # If using PIL image:
             if hasattr(result, "save"):
                 buf = io.BytesIO()
                 result.save(buf, format="PNG")
                 image_data = buf.getvalue()
             else:
                 # Last resort, str (maybe url or b64 already?)
                 if isinstance(result, str):
                     if result.startswith("http"):
                         return ImageResponse(url=result, revised_prompt=request.prompt)
                     # assume b64
                     return ImageResponse(b64_json=result, revised_prompt=request.prompt)
                 else:
                     raise ValueError("Unknown image format returned from service")

        # Convert bytes to base64 string
        b64_img = base64.b64encode(image_data).decode("utf-8")
        
        return ImageResponse(
            b64_json=b64_img,
            revised_prompt=request.prompt # Some models revise prompts, pass through for now
        )

    except Exception as e:
        logger.error(f"Generate image failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}",
        )


@router.post("/edit", response_model=ImageResponse)
async def edit_image(
    prompt: Annotated[str, Form(...)],
    image: Annotated[UploadFile, File(...)],
    current_user: CurrentUser,
    image_service: ImageService = Depends(get_image_service),
):
    """
    Edit an uploaded image based on a text prompt using Google 'Nano Banana Pro'.
    
    Args:
        prompt: Instructions for editing.
        image: The image file to edit.
        current_user: Authenticated user.
        image_service: Service to handle image editing.
        
    Returns:
        ImageResponse with base64 encoded edited image.
    """
    try:
        logger.info(f"Image edit request from user {current_user['uid']}")
        
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format. Supported: JPEG, PNG, WEBP",
            )
        
        # Read image content
        content = await image.read()
        
        # Call service
        result = await image_service.edit_image(prompt, content)
        
        # Process result (similar adaptation logic as generate)
        if isinstance(result, bytes):
            image_data = result
        elif hasattr(result, "_image_bytes"):
             image_data = result._image_bytes
        elif hasattr(result, "image_bytes"):
             image_data = result.image_bytes    
        elif hasattr(result, "save"): # PIL
             buf = io.BytesIO()
             result.save(buf, format="PNG")
             image_data = buf.getvalue()
        else:
             raise ValueError("Unknown image format returned from service")

        b64_img = base64.b64encode(image_data).decode("utf-8")
        
        return ImageResponse(
            b64_json=b64_img,
            revised_prompt=prompt
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit image failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image editing failed: {str(e)}",
        )
