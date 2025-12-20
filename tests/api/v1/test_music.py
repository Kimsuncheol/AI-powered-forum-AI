"""Tests for music generation endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_generate_music_success(authenticated_client):
    """Test successful music generation request."""
    from app.main import app
    from app.api.v1.music import get_music_service
    from app.schemas.music import MusicGenerationResponse
    
    # Create mock service
    mock_service = MagicMock()
    async def fake_generate(prompts, config=None, duration_seconds=30):
        return MusicGenerationResponse(
            audio_b64="YXVkaW9fZGF0YQ==",  # audio_data in base64
            sample_rate_hz=48000,
            channels=2,
            bit_depth=16,
            duration_seconds=30.0,
            prompts_used=[p.text for p in prompts],
        )
    mock_service.generate_music = fake_generate
    
    app.dependency_overrides[get_music_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/music/generate",
        json={
            "prompts": [
                {"text": "minimal techno", "weight": 1.0},
                {"text": "deep bass", "weight": 0.8},
            ],
            "config": {
                "bpm": 120,
                "temperature": 1.0,
            },
            "duration_seconds": 30,
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["audio_b64"] is not None
    assert data["sample_rate_hz"] == 48000
    assert data["channels"] == 2
    assert "minimal techno" in data["prompts_used"]
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_music_unauthorized(client):
    """Test unauthorized music generation request."""
    response = client.post(
        "/api/v1/ai/music/generate",
        json={
            "prompts": [{"text": "test", "weight": 1.0}],
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_generate_music_simple_success(authenticated_client):
    """Test simplified music generation endpoint."""
    from app.main import app
    from app.api.v1.music import get_music_service
    from app.schemas.music import MusicGenerationResponse
    
    mock_service = MagicMock()
    async def fake_generate(prompt_text, bpm=120, duration_seconds=30):
        return MusicGenerationResponse(
            audio_b64="YXVkaW9fZGF0YQ==",
            sample_rate_hz=48000,
            channels=2,
            bit_depth=16,
            duration_seconds=duration_seconds,
            prompts_used=[prompt_text],
        )
    mock_service.generate_music_simple = fake_generate
    
    app.dependency_overrides[get_music_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/music/generate-simple",
        params={
            "prompt": "jazz piano",
            "bpm": 90,
            "duration_seconds": 60,
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "jazz piano" in data["prompts_used"]
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_music_simple_invalid_bpm(authenticated_client):
    """Test simple generation with invalid BPM."""
    response = authenticated_client.post(
        "/api/v1/ai/music/generate-simple",
        params={
            "prompt": "test",
            "bpm": 30,  # Below minimum of 60
            "duration_seconds": 30,
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "bpm" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_music_simple_invalid_duration(authenticated_client):
    """Test simple generation with invalid duration."""
    response = authenticated_client.post(
        "/api/v1/ai/music/generate-simple",
        params={
            "prompt": "test",
            "bpm": 120,
            "duration_seconds": 300,  # Above maximum of 120
        },
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "duration" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_music_invalid_prompt(authenticated_client):
    """Test music generation with invalid prompts."""
    response = authenticated_client.post(
        "/api/v1/ai/music/generate",
        json={
            "prompts": [],  # Empty prompts
            "duration_seconds": 30,
        },
    )
    
    # Should fail validation
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_generate_music_with_full_config(authenticated_client):
    """Test music generation with all config options."""
    from app.main import app
    from app.api.v1.music import get_music_service
    from app.schemas.music import MusicGenerationResponse
    
    mock_service = MagicMock()
    async def fake_generate(prompts, config=None, duration_seconds=30):
        return MusicGenerationResponse(
            audio_b64="YXVkaW9fZGF0YQ==",
            sample_rate_hz=48000,
            channels=2,
            bit_depth=16,
            duration_seconds=duration_seconds,
            prompts_used=[p.text for p in prompts],
        )
    mock_service.generate_music = fake_generate
    
    app.dependency_overrides[get_music_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/music/generate",
        json={
            "prompts": [{"text": "ambient", "weight": 1.0}],
            "config": {
                "bpm": 80,
                "temperature": 0.8,
                "guidance": 3.0,
                "density": 0.3,
                "brightness": 0.7,
                "scale": "C_MAJOR_A_MINOR",
                "mute_drums": True,
                "music_generation_mode": "DIVERSITY",
            },
            "duration_seconds": 30,
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_generate_music_service_unavailable(authenticated_client):
    """Test music generation when service is unavailable."""
    from app.main import app
    from app.api.v1.music import get_music_service
    
    mock_service = MagicMock()
    async def fake_generate(prompts, config=None, duration_seconds=30):
        raise RuntimeError("Google API client not initialized")
    mock_service.generate_music = fake_generate
    
    app.dependency_overrides[get_music_service] = lambda: mock_service
    
    response = authenticated_client.post(
        "/api/v1/ai/music/generate",
        json={
            "prompts": [{"text": "test", "weight": 1.0}],
        },
    )
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    app.dependency_overrides = {}
