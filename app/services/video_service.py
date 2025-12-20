"""Service for Google Veo 3.1 video generation."""

import asyncio
import base64
import logging
from typing import Optional, Tuple

from google import genai
from google.genai import types

from app.config import settings
from app.schemas.video import (
    OperationStatus,
    VideoGenerationConfig,
    VideoGenerationResponse,
    VideoOperationStatusResponse,
)

logger = logging.getLogger(__name__)


class VideoService:
    """Service to handle video generation using Google Veo 3.1."""

    def __init__(self):
        """Initialize the service with API key."""
        if settings.GOOGLE_API_KEY:
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        else:
            logger.warning("GOOGLE_API_KEY not set. Video features will fail.")
            self.client = None
            
        self.model_name = settings.GOOGLE_VIDEO_MODEL
        # Store operations for status polling
        self._operations: dict = {}

    async def generate_video(
        self,
        prompt: str,
        config: Optional[VideoGenerationConfig] = None,
    ) -> VideoGenerationResponse:
        """
        Generate a video from a text prompt using Veo 3.1.
        
        Args:
            prompt: Text description of the video to generate.
            config: Video generation configuration.
            
        Returns:
            VideoGenerationResponse with operation ID for polling.
            
        Raises:
            Exception: If generation fails to start.
        """
        if not self.client:
            raise RuntimeError("Google API client not initialized")
        
        try:
            config = config or VideoGenerationConfig()
            
            # Build generation config
            gen_config = types.GenerateVideosConfig(
                aspect_ratio=config.aspect_ratio.value,
                resolution=config.resolution.value,
                duration_seconds=int(config.duration_seconds.value),
                person_generation=config.person_generation.value,
            )
            
            if config.negative_prompt:
                gen_config.negative_prompt = config.negative_prompt
            if config.seed is not None:
                gen_config.seed = config.seed
            
            # Start async video generation
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt,
                config=gen_config,
            )
            
            # Store operation for later polling
            operation_id = str(id(operation))
            self._operations[operation_id] = operation
            
            logger.info(f"Started video generation operation: {operation_id}")
            
            return VideoGenerationResponse(
                operation_id=operation_id,
                status=OperationStatus.PROCESSING,
            )

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise e

    async def generate_video_from_image(
        self,
        prompt: str,
        image_bytes: bytes,
        config: Optional[VideoGenerationConfig] = None,
    ) -> VideoGenerationResponse:
        """
        Generate a video from an image (image-to-video).
        
        Args:
            prompt: Text description of the animation/motion.
            image_bytes: The source image as bytes.
            config: Video generation configuration.
            
        Returns:
            VideoGenerationResponse with operation ID for polling.
        """
        if not self.client:
            raise RuntimeError("Google API client not initialized")
        
        try:
            config = config or VideoGenerationConfig()
            
            # Create image object from bytes
            image = types.Image(image_bytes=image_bytes)
            
            gen_config = types.GenerateVideosConfig(
                aspect_ratio=config.aspect_ratio.value,
                resolution=config.resolution.value,
                duration_seconds=int(config.duration_seconds.value),
                person_generation=config.person_generation.value,
            )
            
            if config.negative_prompt:
                gen_config.negative_prompt = config.negative_prompt
            if config.seed is not None:
                gen_config.seed = config.seed
            
            # Start async video generation with image
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt,
                image=image,
                config=gen_config,
            )
            
            operation_id = str(id(operation))
            self._operations[operation_id] = operation
            
            logger.info(f"Started image-to-video generation: {operation_id}")
            
            return VideoGenerationResponse(
                operation_id=operation_id,
                status=OperationStatus.PROCESSING,
            )

        except Exception as e:
            logger.error(f"Image-to-video generation failed: {e}")
            raise e

    async def get_operation_status(
        self,
        operation_id: str,
    ) -> VideoOperationStatusResponse:
        """
        Check the status of a video generation operation.
        
        Args:
            operation_id: The operation ID to check.
            
        Returns:
            VideoOperationStatusResponse with current status.
        """
        if operation_id not in self._operations:
            return VideoOperationStatusResponse(
                operation_id=operation_id,
                done=False,
                status=OperationStatus.FAILED,
                error_message="Operation not found",
            )
        
        try:
            operation = self._operations[operation_id]
            
            # Refresh operation status
            operation = self.client.operations.get(operation)
            self._operations[operation_id] = operation
            
            if operation.done:
                # Operation completed
                try:
                    generated_video = operation.response.generated_videos[0]
                    
                    # Download the video
                    self.client.files.download(file=generated_video.video)
                    
                    # Get video bytes and encode to base64
                    video_bytes = generated_video.video._downloaded_bytes
                    video_b64 = base64.b64encode(video_bytes).decode("utf-8")
                    
                    # Clean up stored operation
                    del self._operations[operation_id]
                    
                    return VideoOperationStatusResponse(
                        operation_id=operation_id,
                        done=True,
                        status=OperationStatus.COMPLETED,
                        video_b64=video_b64,
                    )
                except Exception as e:
                    logger.error(f"Failed to retrieve video: {e}")
                    return VideoOperationStatusResponse(
                        operation_id=operation_id,
                        done=True,
                        status=OperationStatus.FAILED,
                        error_message=str(e),
                    )
            else:
                return VideoOperationStatusResponse(
                    operation_id=operation_id,
                    done=False,
                    status=OperationStatus.PROCESSING,
                )

        except Exception as e:
            logger.error(f"Failed to get operation status: {e}")
            return VideoOperationStatusResponse(
                operation_id=operation_id,
                done=False,
                status=OperationStatus.FAILED,
                error_message=str(e),
            )

    async def generate_video_sync(
        self,
        prompt: str,
        config: Optional[VideoGenerationConfig] = None,
        timeout_seconds: int = 300,
        poll_interval: int = 10,
    ) -> Tuple[bytes, str]:
        """
        Generate a video synchronously (blocking until complete).
        
        Args:
            prompt: Text description of the video.
            config: Video generation configuration.
            timeout_seconds: Maximum time to wait.
            poll_interval: Seconds between status checks.
            
        Returns:
            Tuple of (video_bytes, operation_id).
            
        Raises:
            TimeoutError: If generation takes too long.
            Exception: If generation fails.
        """
        response = await self.generate_video(prompt, config)
        operation_id = response.operation_id
        
        elapsed = 0
        while elapsed < timeout_seconds:
            status = await self.get_operation_status(operation_id)
            
            if status.done:
                if status.status == OperationStatus.COMPLETED and status.video_b64:
                    return base64.b64decode(status.video_b64), operation_id
                else:
                    raise Exception(status.error_message or "Video generation failed")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Video generation timed out after {timeout_seconds}s")
