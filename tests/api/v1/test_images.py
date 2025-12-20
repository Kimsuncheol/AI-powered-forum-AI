"""Tests for image generation endpoints."""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


@pytest.fixture
def mock_image_service():
    """Mock image service to avoid real API calls."""
    # We mock the dependency provider in the router module
    with patch("app.api.v1.images.ImageService") as mock_class:
        mock_instance = mock_class.return_value
        # Mock generate_image returning bytes
        mock_instance.generate_image = MagicMock()
        async def async_gen(prompt):
            return b"fake_image_bytes"
        mock_instance.generate_image.side_effect = async_gen

        # Mock edit_image returning bytes
        mock_instance.edit_image = MagicMock()
        async def async_edit(prompt, img_bytes):
            return b"fake_edited_image"
        mock_instance.edit_image.side_effect = async_edit
        
        yield mock_instance


@pytest.mark.asyncio
async def test_generate_image_success(authenticated_client):
    """Test successful image generation."""
    # Override dependency directly
    from app.main import app
    from app.api.v1.images import get_image_service
    
    # Create mock that returns bytes
    mock_service = MagicMock()
    async def fake_gen(prompt):
        return b"fake_generated_bytes"
    mock_service.generate_image.side_effect = fake_gen
    
    app.dependency_overrides[get_image_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/images/generate",
        json={"prompt": "A beautiful sunset"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["b64_json"] is not None
    # "fake_generated_bytes" b64 encoded
    assert data["revised_prompt"] == "A beautiful sunset"
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_image_unauthorized(client):
    """Test unauthorized generation request."""
    response = client.post(
        "/api/v1/ai/images/generate",
        json={"prompt": "A secret image"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_edit_image_success(authenticated_client):
    """Test successful image editing."""
    # Override dependency
    from app.main import app
    from app.api.v1.images import get_image_service
    
    mock_service = MagicMock()
    async def fake_edit(prompt, image_bytes):
        return b"fake_edited_bytes"
    mock_service.edit_image.side_effect = fake_edit
    
    app.dependency_overrides[get_image_service] = lambda: mock_service
    
    # Create fake file
    file_content = b"fake_input_image"
    files = {"image": ("test.png", file_content, "image/png")}
    data = {"prompt": "Make it futuristic"}
    
    response = authenticated_client.post(
        "/api/v1/ai/images/edit",
        data=data,
        files=files,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["b64_json"] is not None
    assert data["revised_prompt"] == "Make it futuristic"
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_edit_image_invalid_file_type(authenticated_client):
    """Test upload of invalid file type."""
    file_content = b"fake_text_file"
    files = {"image": ("test.txt", file_content, "text/plain")}
    data = {"prompt": "Fix this"}
    
    response = authenticated_client.post(
        "/api/v1/ai/images/edit",
        data=data,
        files=files,
    )
    
    # FastApi/Starlette UploadFile validation or custom check
    # Check what status code is returned.
    # The endpoint explicit check raises 400.
    assert response.status_code == status.HTTP_400_BAD_REQUEST
