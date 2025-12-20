"""Video generation endpoints using Google Veo 3.1."""

import base64
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.deps import CurrentUser
from app.schemas.video import (
    VideoFromImageRequest,
    VideoGenerationConfig,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoOperationStatusResponse,
)
from app.services.video_service import VideoService

router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton instance for operation tracking
_video_service: VideoService | None = None


def get_video_service() -> VideoService:
    """Dependency to get video service instance."""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: CurrentUser,
    video_service: VideoService = Depends(get_video_service),
):
    """
    Generate a video from a text prompt using Google Veo 3.1.
    
    This starts an asynchronous video generation operation.
    Use the returned operation_id to poll for status.
    
    Args:
        request: Contains the text prompt and optional config.
        current_user: Authenticated user.
        video_service: Service to handle video generation.
        
    Returns:
        VideoGenerationResponse with operation_id for polling.
    """
    try:
        logger.info(f"Video generation request from user {current_user['uid']}")
        
        response = await video_service.generate_video(
            prompt=request.prompt,
            config=request.config,
        )
        
        return response

    except RuntimeError as e:
        logger.error(f"Video service not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Video generation service not available",
        )
    except Exception as e:
        logger.error(f"Generate video failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}",
        )


@router.post("/generate-from-image", response_model=VideoGenerationResponse)
async def generate_video_from_image(
    prompt: Annotated[str, Form(...)],
    image: Annotated[UploadFile, File(...)],
    current_user: CurrentUser,
    video_service: VideoService = Depends(get_video_service),
    aspect_ratio: Annotated[str | None, Form()] = None,
    resolution: Annotated[str | None, Form()] = None,
    duration_seconds: Annotated[str | None, Form()] = None,
    negative_prompt: Annotated[str | None, Form()] = None,
):
    """
    Generate a video from an image (image-to-video) using Veo 3.1.
    
    Upload an image and provide a prompt describing the animation/motion.
    
    Args:
        prompt: Text describing the animation.
        image: The source image file.
        current_user: Authenticated user.
        video_service: Service to handle video generation.
        
    Returns:
        VideoGenerationResponse with operation_id for polling.
    """
    try:
        logger.info(f"Image-to-video request from user {current_user['uid']}")
        
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format. Supported: JPEG, PNG, WEBP",
            )
        
        # Read image content
        image_bytes = await image.read()
        
        # Build config from form fields
        config = VideoGenerationConfig()
        if aspect_ratio:
            config.aspect_ratio = aspect_ratio
        if resolution:
            config.resolution = resolution
        if duration_seconds:
            config.duration_seconds = duration_seconds
        if negative_prompt:
            config.negative_prompt = negative_prompt
        
        response = await video_service.generate_video_from_image(
            prompt=prompt,
            image_bytes=image_bytes,
            config=config,
        )
        
        return response

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Video service not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Video generation service not available",
        )
    except Exception as e:
        logger.error(f"Image-to-video failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image-to-video generation failed: {str(e)}",
        )


@router.get("/status/{operation_id}", response_model=VideoOperationStatusResponse)
async def get_video_status(
    operation_id: str,
    current_user: CurrentUser,
    video_service: VideoService = Depends(get_video_service),
):
    """
    Check the status of a video generation operation.
    
    Poll this endpoint until 'done' is True, then retrieve the video.
    
    Args:
        operation_id: The operation ID from the generate request.
        current_user: Authenticated user.
        video_service: Service to handle video generation.
        
    Returns:
        VideoOperationStatusResponse with current status and video if complete.
    """
    try:
        logger.info(
            f"Video status check from user {current_user['uid']}: {operation_id}"
        )
        
        response = await video_service.get_operation_status(operation_id)
        
        return response

    except Exception as e:
        logger.error(f"Get video status failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operation status: {str(e)}",
        )
