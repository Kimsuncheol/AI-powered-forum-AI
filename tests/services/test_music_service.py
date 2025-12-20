"""Tests for music service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.music import (
    MusicGenerationConfig,
    MusicGenerationResponse,
    WeightedPrompt,
)


@pytest.fixture
def mock_genai_client():
    """Mock the Google GenAI client with async music session."""
    with patch("app.services.music_service.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        
        # Mock async context manager for music session
        mock_session = AsyncMock()
        mock_session.set_weighted_prompts = AsyncMock()
        mock_session.set_music_generation_config = AsyncMock()
        mock_session.play = AsyncMock()
        mock_session.stop = AsyncMock()
        
        # Mock receive to yield some audio chunks then stop
        async def mock_receive():
            for _ in range(3):
                mock_message = MagicMock()
                mock_message.server_content = MagicMock()
                mock_message.server_content.audio_chunks = [
                    MagicMock(data=b"audio_chunk_data")
                ]
                yield mock_message
        
        mock_session.receive = mock_receive
        
        # Setup async context manager
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client.aio.live.music.connect.return_value = mock_context
        
        yield mock_client


@pytest.fixture
def music_service(mock_genai_client):
    """Create music service with mocked client."""
    with patch("app.services.music_service.settings") as mock_settings:
        mock_settings.GOOGLE_API_KEY = "test-api-key"
        mock_settings.GOOGLE_MUSIC_MODEL = "models/lyria-realtime-exp"
        
        from app.services.music_service import MusicService
        service = MusicService()
        service.client = mock_genai_client
        return service


@pytest.mark.asyncio
async def test_generate_music_success(music_service):
    """Test successful music generation."""
    prompts = [
        WeightedPrompt(text="minimal techno", weight=1.0),
        WeightedPrompt(text="deep bass", weight=0.8),
    ]
    config = MusicGenerationConfig(bpm=120)
    
    # Mock sleep to speed up test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await music_service.generate_music(
            prompts=prompts,
            config=config,
            duration_seconds=5,  # Short duration for test
        )
    
    assert isinstance(response, MusicGenerationResponse)
    assert response.audio_b64 is not None
    assert response.sample_rate_hz == 48000
    assert response.channels == 2
    assert response.bit_depth == 16
    assert "minimal techno" in response.prompts_used


@pytest.mark.asyncio
async def test_generate_music_simple(music_service):
    """Test simplified music generation."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await music_service.generate_music_simple(
            prompt_text="jazz piano",
            bpm=90,
            duration_seconds=5,
        )
    
    assert isinstance(response, MusicGenerationResponse)
    assert "jazz piano" in response.prompts_used


@pytest.mark.asyncio
async def test_generate_music_with_all_config_options(music_service):
    """Test music generation with full configuration."""
    from app.schemas.music import MusicGenerationMode, MusicScale
    
    prompts = [WeightedPrompt(text="ambient", weight=1.0)]
    config = MusicGenerationConfig(
        bpm=80,
        temperature=0.8,
        guidance=3.0,
        density=0.3,
        brightness=0.7,
        scale=MusicScale.C_MAJOR_A_MINOR,
        mute_drums=True,
        music_generation_mode=MusicGenerationMode.DIVERSITY,
    )
    
    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await music_service.generate_music(
            prompts=prompts,
            config=config,
            duration_seconds=5,
        )
    
    assert isinstance(response, MusicGenerationResponse)


@pytest.mark.asyncio
async def test_generate_music_no_client():
    """Test error when client is not initialized."""
    with patch("app.services.music_service.settings") as mock_settings:
        mock_settings.GOOGLE_API_KEY = ""
        mock_settings.GOOGLE_MUSIC_MODEL = "models/lyria-realtime-exp"
        
        from app.services.music_service import MusicService
        service = MusicService()
        service.client = None
        
        prompts = [WeightedPrompt(text="test", weight=1.0)]
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await service.generate_music(prompts=prompts)


def test_weighted_prompt_validation():
    """Test WeightedPrompt model validation."""
    # Valid prompt
    prompt = WeightedPrompt(text="rock guitar", weight=2.0)
    assert prompt.text == "rock guitar"
    assert prompt.weight == 2.0
    
    # Weight must be positive
    with pytest.raises(ValueError):
        WeightedPrompt(text="test", weight=0)
    
    # Weight must not exceed 5.0
    with pytest.raises(ValueError):
        WeightedPrompt(text="test", weight=6.0)


def test_music_generation_config_validation():
    """Test MusicGenerationConfig validation."""
    # Valid config
    config = MusicGenerationConfig(bpm=120, density=0.5)
    assert config.bpm == 120
    
    # BPM out of range
    with pytest.raises(ValueError):
        MusicGenerationConfig(bpm=50)  # Below 60
    
    with pytest.raises(ValueError):
        MusicGenerationConfig(bpm=250)  # Above 200
    
    # Density out of range
    with pytest.raises(ValueError):
        MusicGenerationConfig(density=1.5)  # Above 1.0
