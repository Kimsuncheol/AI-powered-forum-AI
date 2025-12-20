"""Tests for video service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.video import (
    OperationStatus,
    VideoGenerationConfig,
    VideoGenerationResponse,
    VideoOperationStatusResponse,
)


@pytest.fixture
def mock_genai_client():
    """Mock the Google GenAI client."""
    with patch("app.services.video_service.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        yield mock_client


@pytest.fixture
def video_service(mock_genai_client):
    """Create video service with mocked client."""
    with patch("app.services.video_service.settings") as mock_settings:
        mock_settings.GOOGLE_API_KEY = "test-api-key"
        mock_settings.GOOGLE_VIDEO_MODEL = "veo-3.1-generate-preview"
        
        from app.services.video_service import VideoService
        service = VideoService()
        service.client = mock_genai_client
        return service


@pytest.mark.asyncio
async def test_generate_video_success(video_service, mock_genai_client):
    """Test successful video generation start."""
    # Setup mock operation
    mock_operation = MagicMock()
    mock_operation.done = False
    mock_genai_client.models.generate_videos.return_value = mock_operation
    
    # Call service
    response = await video_service.generate_video(
        prompt="A beautiful sunset over the ocean",
        config=VideoGenerationConfig(),
    )
    
    # Verify
    assert isinstance(response, VideoGenerationResponse)
    assert response.operation_id is not None
    assert response.status == OperationStatus.PROCESSING
    assert mock_genai_client.models.generate_videos.called


@pytest.mark.asyncio
async def test_generate_video_with_config(video_service, mock_genai_client):
    """Test video generation with custom config."""
    mock_operation = MagicMock()
    mock_operation.done = False
    mock_genai_client.models.generate_videos.return_value = mock_operation
    
    config = VideoGenerationConfig(
        negative_prompt="low quality, blurry",
        seed=42,
    )
    
    response = await video_service.generate_video(
        prompt="Test prompt",
        config=config,
    )
    
    assert response.status == OperationStatus.PROCESSING
    
    # Verify config was passed
    call_kwargs = mock_genai_client.models.generate_videos.call_args
    assert call_kwargs is not None


@pytest.mark.asyncio
async def test_generate_video_from_image_success(video_service, mock_genai_client):
    """Test image-to-video generation."""
    mock_operation = MagicMock()
    mock_operation.done = False
    mock_genai_client.models.generate_videos.return_value = mock_operation
    
    response = await video_service.generate_video_from_image(
        prompt="Slow pan across the scene",
        image_bytes=b"fake_image_data",
        config=VideoGenerationConfig(),
    )
    
    assert isinstance(response, VideoGenerationResponse)
    assert response.operation_id is not None
    assert response.status == OperationStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_operation_status_processing(video_service, mock_genai_client):
    """Test status check for in-progress operation."""
    # First start an operation
    mock_operation = MagicMock()
    mock_operation.done = False
    mock_genai_client.models.generate_videos.return_value = mock_operation
    mock_genai_client.operations.get.return_value = mock_operation
    
    gen_response = await video_service.generate_video(
        prompt="Test",
    )
    
    # Check status
    status = await video_service.get_operation_status(gen_response.operation_id)
    
    assert isinstance(status, VideoOperationStatusResponse)
    assert status.done is False
    assert status.status == OperationStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_operation_status_not_found(video_service):
    """Test status check for non-existent operation."""
    status = await video_service.get_operation_status("non-existent-id")
    
    assert status.done is False
    assert status.status == OperationStatus.FAILED
    assert "not found" in status.error_message.lower()


@pytest.mark.asyncio
async def test_generate_video_no_client():
    """Test error when client is not initialized."""
    with patch("app.services.video_service.settings") as mock_settings:
        mock_settings.GOOGLE_API_KEY = ""
        mock_settings.GOOGLE_VIDEO_MODEL = "veo-3.1-generate-preview"
        
        from app.services.video_service import VideoService
        service = VideoService()
        service.client = None
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await service.generate_video(prompt="Test")
