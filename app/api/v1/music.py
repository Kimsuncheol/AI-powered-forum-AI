"""Music generation endpoints using Google Lyria RealTime."""

import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.deps import CurrentUser
from app.schemas.music import (
    MusicGenerationRequest,
    MusicGenerationResponse,
)
from app.services.music_service import MusicService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_music_service() -> MusicService:
    """Dependency to get music service instance."""
    return MusicService()


@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    request: MusicGenerationRequest,
    current_user: CurrentUser,
    music_service: MusicService = Depends(get_music_service),
):
    """
    Generate music from weighted prompts using Google Lyria RealTime.
    
    Connects to Lyria via WebSocket, generates audio for the specified
    duration, and returns the audio as base64 encoded PCM16 data.
    
    Args:
        request: Contains prompts, config, and duration.
        current_user: Authenticated user.
        music_service: Service to handle music generation.
        
    Returns:
        MusicGenerationResponse with base64 encoded audio data.
    """
    try:
        logger.info(
            f"Music generation request from user {current_user['uid']}: "
            f"{len(request.prompts)} prompts, {request.duration_seconds}s"
        )
        
        response = await music_service.generate_music(
            prompts=request.prompts,
            config=request.config,
            duration_seconds=request.duration_seconds,
        )
        
        logger.info(
            f"Generated {response.duration_seconds:.2f}s of music for user "
            f"{current_user['uid']}"
        )
        
        return response

    except RuntimeError as e:
        logger.error(f"Music service not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Music generation service not available",
        )
    except Exception as e:
        logger.error(f"Generate music failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Music generation failed: {str(e)}",
        )


@router.post("/generate-simple", response_model=MusicGenerationResponse)
async def generate_music_simple(
    prompt: str,
    current_user: CurrentUser,
    music_service: MusicService = Depends(get_music_service),
    bpm: int = 120,
    duration_seconds: int = 30,
):
    """
    Simplified music generation with a single text prompt.
    
    Args:
        prompt: Text describing the music style.
        current_user: Authenticated user.
        music_service: Service to handle music generation.
        bpm: Beats per minute (60-200).
        duration_seconds: Duration to generate (5-120).
        
    Returns:
        MusicGenerationResponse with base64 encoded audio data.
    """
    try:
        # Validate parameters
        if not 60 <= bpm <= 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BPM must be between 60 and 200",
            )
        if not 5 <= duration_seconds <= 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration must be between 5 and 120 seconds",
            )
        
        logger.info(
            f"Simple music generation from user {current_user['uid']}: "
            f"'{prompt[:50]}...', {bpm} BPM, {duration_seconds}s"
        )
        
        response = await music_service.generate_music_simple(
            prompt_text=prompt,
            bpm=bpm,
            duration_seconds=duration_seconds,
        )
        
        return response

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Music service not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Music generation service not available",
        )
    except Exception as e:
        logger.error(f"Generate simple music failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Music generation failed: {str(e)}",
        )
