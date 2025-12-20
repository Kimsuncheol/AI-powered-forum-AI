"""Tests for video generation endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from app.schemas.video import OperationStatus


@pytest.fixture
def mock_video_service():
    """Mock video service for endpoint tests."""
    with patch("app.api.v1.videos.get_video_service") as mock_getter:
        mock_service = MagicMock()
        mock_getter.return_value = mock_service
        yield mock_service


@pytest.mark.asyncio
async def test_generate_video_success(authenticated_client):
    """Test successful video generation request."""
    from app.main import app
    from app.api.v1.videos import get_video_service
    from app.schemas.video import VideoGenerationResponse
    
    # Create mock service
    mock_service = MagicMock()
    async def fake_generate(prompt, config=None):
        return VideoGenerationResponse(
            operation_id="test-op-123",
            status=OperationStatus.PROCESSING,
        )
    mock_service.generate_video = fake_generate
    
    app.dependency_overrides[get_video_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/videos/generate",
        json={"prompt": "A beautiful sunset over the ocean"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["operation_id"] == "test-op-123"
    assert data["status"] == "processing"
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_video_unauthorized(client):
    """Test unauthorized video generation request."""
    response = client.post(
        "/api/v1/ai/videos/generate",
        json={"prompt": "Test prompt"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_generate_video_from_image_success(authenticated_client):
    """Test successful image-to-video generation."""
    from app.main import app
    from app.api.v1.videos import get_video_service
    from app.schemas.video import VideoGenerationResponse
    
    mock_service = MagicMock()
    async def fake_generate(prompt, image_bytes, config=None):
        return VideoGenerationResponse(
            operation_id="test-img-op-456",
            status=OperationStatus.PROCESSING,
        )
    mock_service.generate_video_from_image = fake_generate
    
    app.dependency_overrides[get_video_service] = lambda: mock_service
    
    file_content = b"fake_image_data"
    files = {"image": ("test.png", file_content, "image/png")}
    data = {"prompt": "Slow pan across the scene"}
    
    response = authenticated_client.post(
        "/api/v1/ai/videos/generate-from-image",
        data=data,
        files=files,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["operation_id"] == "test-img-op-456"
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_video_from_image_invalid_type(authenticated_client):
    """Test upload of invalid file type for image-to-video."""
    file_content = b"not an image"
    files = {"image": ("test.txt", file_content, "text/plain")}
    data = {"prompt": "Test prompt"}
    
    response = authenticated_client.post(
        "/api/v1/ai/videos/generate-from-image",
        data=data,
        files=files,
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_video_status_processing(authenticated_client):
    """Test video status check for in-progress operation."""
    from app.main import app
    from app.api.v1.videos import get_video_service
    from app.schemas.video import VideoOperationStatusResponse
    
    mock_service = MagicMock()
    async def fake_status(operation_id):
        return VideoOperationStatusResponse(
            operation_id=operation_id,
            done=False,
            status=OperationStatus.PROCESSING,
        )
    mock_service.get_operation_status = fake_status
    
    app.dependency_overrides[get_video_service] = lambda: mock_service
    
    response = authenticated_client.get(
        "/api/v1/ai/videos/status/test-op-123",
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["operation_id"] == "test-op-123"
    assert data["done"] is False
    assert data["status"] == "processing"
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_video_status_completed(authenticated_client):
    """Test video status check for completed operation."""
    from app.main import app
    from app.api.v1.videos import get_video_service
    from app.schemas.video import VideoOperationStatusResponse
    
    mock_service = MagicMock()
    async def fake_status(operation_id):
        return VideoOperationStatusResponse(
            operation_id=operation_id,
            done=True,
            status=OperationStatus.COMPLETED,
            video_b64="YmFzZTY0X3ZpZGVvX2RhdGE=",  # base64_video_data
        )
    mock_service.get_operation_status = fake_status
    
    app.dependency_overrides[get_video_service] = lambda: mock_service
    
    response = authenticated_client.get(
        "/api/v1/ai/videos/status/completed-op",
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["done"] is True
    assert data["status"] == "completed"
    assert data["video_b64"] is not None
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_video_status_unauthorized(client):
    """Test unauthorized status check."""
    response = client.get(
        "/api/v1/ai/videos/status/test-op",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
