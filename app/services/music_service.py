"""Service for Google Lyria RealTime music generation."""

import asyncio
import base64
import logging
from typing import List, Optional

from google import genai
from google.genai import types

from app.config import settings
from app.schemas.music import (
    MusicGenerationConfig,
    MusicGenerationResponse,
    WeightedPrompt,
)

logger = logging.getLogger(__name__)


class MusicService:
    """Service to handle music generation using Google Lyria RealTime."""

    def __init__(self):
        """Initialize the service with API key."""
        if settings.GOOGLE_API_KEY:
            # Lyria requires v1alpha API version
            self.client = genai.Client(
                api_key=settings.GOOGLE_API_KEY,
                http_options={"api_version": "v1alpha"},
            )
        else:
            logger.warning("GOOGLE_API_KEY not set. Music features will fail.")
            self.client = None
            
        self.model_name = settings.GOOGLE_MUSIC_MODEL
        self.sample_rate_hz = 48000
        self.channels = 2
        self.bit_depth = 16

    async def generate_music(
        self,
        prompts: List[WeightedPrompt],
        config: Optional[MusicGenerationConfig] = None,
        duration_seconds: int = 30,
    ) -> MusicGenerationResponse:
        """
        Generate music from weighted prompts.
        
        This connects to Lyria RealTime via WebSocket, starts generation,
        collects audio chunks for the specified duration, then returns.
        
        Args:
            prompts: List of weighted prompts describing the music.
            config: Music generation configuration.
            duration_seconds: How long to generate audio for.
            
        Returns:
            MusicGenerationResponse with base64 encoded audio.
            
        Raises:
            Exception: If generation fails.
        """
        if not self.client:
            raise RuntimeError("Google API client not initialized")
        
        config = config or MusicGenerationConfig()
        audio_chunks: List[bytes] = []
        
        try:
            async def receive_audio(session):
                """Background task to collect audio chunks."""
                nonlocal audio_chunks
                try:
                    async for message in session.receive():
                        if hasattr(message, "server_content") and message.server_content:
                            if hasattr(message.server_content, "audio_chunks"):
                                for chunk in message.server_content.audio_chunks:
                                    audio_chunks.append(chunk.data)
                except asyncio.CancelledError:
                    pass  # Expected when we stop receiving

            # Connect to Lyria RealTime
            async with self.client.aio.live.music.connect(
                model=self.model_name
            ) as session:
                # Start receive task
                receive_task = asyncio.create_task(receive_audio(session))
                
                # Set weighted prompts
                await session.set_weighted_prompts(
                    prompts=[
                        types.WeightedPrompt(text=p.text, weight=p.weight)
                        for p in prompts
                    ]
                )
                
                # Build music generation config
                music_config = types.LiveMusicGenerationConfig(
                    bpm=config.bpm,
                    temperature=config.temperature,
                    guidance=config.guidance,
                )
                
                if config.density is not None:
                    music_config.density = config.density
                if config.brightness is not None:
                    music_config.brightness = config.brightness
                if config.scale is not None:
                    music_config.scale = getattr(types.Scale, config.scale.value, None)
                
                music_config.mute_bass = config.mute_bass
                music_config.mute_drums = config.mute_drums
                music_config.only_bass_and_drums = config.only_bass_and_drums
                music_config.music_generation_mode = getattr(
                    types.MusicGenerationMode, 
                    config.music_generation_mode.value,
                    types.MusicGenerationMode.QUALITY,
                )
                
                await session.set_music_generation_config(config=music_config)
                
                # Start streaming
                await session.play()
                
                # Collect audio for the specified duration
                await asyncio.sleep(duration_seconds)
                
                # Stop and cleanup
                await session.stop()
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass

            # Combine all audio chunks
            combined_audio = b"".join(audio_chunks)
            audio_b64 = base64.b64encode(combined_audio).decode("utf-8")
            
            # Calculate actual duration based on audio data
            # PCM16 stereo at 48kHz = 48000 * 2 channels * 2 bytes = 192000 bytes/sec
            bytes_per_second = self.sample_rate_hz * self.channels * (self.bit_depth // 8)
            actual_duration = len(combined_audio) / bytes_per_second if bytes_per_second > 0 else 0
            
            logger.info(
                f"Generated {actual_duration:.2f}s of music from {len(prompts)} prompts"
            )
            
            return MusicGenerationResponse(
                audio_b64=audio_b64,
                sample_rate_hz=self.sample_rate_hz,
                channels=self.channels,
                bit_depth=self.bit_depth,
                duration_seconds=actual_duration,
                prompts_used=[p.text for p in prompts],
            )

        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            raise e

    async def generate_music_simple(
        self,
        prompt_text: str,
        bpm: int = 120,
        duration_seconds: int = 30,
    ) -> MusicGenerationResponse:
        """
        Simplified music generation with a single prompt.
        
        Args:
            prompt_text: Text describing the music style.
            bpm: Beats per minute.
            duration_seconds: Duration to generate.
            
        Returns:
            MusicGenerationResponse with audio data.
        """
        prompts = [WeightedPrompt(text=prompt_text, weight=1.0)]
        config = MusicGenerationConfig(bpm=bpm)
        return await self.generate_music(prompts, config, duration_seconds)
