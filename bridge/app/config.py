"""
Configuration for the VisionClaw-Ollama bridge.

Reads from environment (with .env support via pydantic-settings).
Service URLs default to the already-deployed local services per DECISIONS.md D4.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bridge configuration. Override via env vars or a .env file in the bridge/ dir."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service URLs
    ollama_url: str = "http://localhost:11434"
    # Use local models for real-time. Cloud models (qwen3.5:397b-cloud) are
    # too slow for the spike (60s+ timeouts) and would tank the voice latency.
    ollama_chat_model: str = "hoangquan456/qwen3-nothink:4b"  # local, fast
    ollama_vision_model: str = "llava:7b"  # for images
    speaches_url: str = "http://192.168.4.12:8000"
    speaches_stt_model: str = "Systran/faster-whisper-base"  # fast, accurate enough
    speaches_tts_model: str = "hexgrad/Kokoro-82M"  # local neural TTS, low latency
    openclaw_gateway_url: str = "http://localhost:18789"

    # Bridge server
    bridge_host: str = "0.0.0.0"
    bridge_port: int = 7860

    # Audio config (matches upstream GeminiConfig.kt)
    input_audio_sample_rate: int = 16000
    output_audio_sample_rate: int = 24000
    audio_channels: int = 1
    audio_bits_per_sample: int = 16

    # Vision config (matches upstream GeminiConfig.kt)
    video_frame_interval_ms: int = 1000
    video_jpeg_quality: int = 50

    # Logging
    log_level: str = "INFO"


# Global settings instance — imported by other modules
settings = Settings()
