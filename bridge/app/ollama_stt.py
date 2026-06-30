"""
Speaches STT/TTS client.

Speaches is the OpenAI-compatible audio API we already run on the Jetson
(192.168.4.12:8000). It exposes:
  - POST /v1/audio/transcriptions  (Whisper STT)
  - POST /v1/audio/speech          (Kokoro / Piper TTS)

We use it for both directions in the bridge.
"""

from __future__ import annotations

import base64
import logging
import httpx
from .config import settings

log = logging.getLogger(__name__)


async def transcribe_pcm(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    """
    Transcribe PCM audio bytes (mono 16-bit) to text using Speaches/Whisper.
    Returns the recognized text, or "" if no speech detected.
    """
    # Speaches expects a file-like upload. We wrap the PCM in a WAV container
    # so it has a real header.
    wav_bytes = _pcm_to_wav(audio_bytes, sample_rate=sample_rate)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.speaches_url}/v1/audio/transcriptions",
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": settings.speaches_stt_model, "response_format": "json"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("text", "").strip()


async def synthesize_speech(text: str) -> bytes:
    """
    Synthesize text to PCM audio bytes (mono, output sample rate).
    Returns raw PCM bytes (no WAV header — Gemini protocol wants raw PCM).
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.speaches_url}/v1/audio/speech",
            json={
                "model": settings.speaches_tts_model,
                "input": text,
                "voice": "af_heart",  # Kokoro default
                "response_format": "pcm",
                "sample_rate": settings.output_audio_sample_rate,
            },
        )
        resp.raise_for_status()
        return resp.content


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """Wrap raw PCM bytes in a minimal WAV header so Speaches can read it."""
    import struct
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + pcm_bytes


def decode_base64_audio(b64: str) -> bytes:
    """Decode base64 audio data from a Gemini Bidi message."""
    return base64.b64decode(b64)


def encode_base64_audio(audio_bytes: bytes) -> str:
    """Encode audio bytes to base64 for the Gemini Bidi response."""
    return base64.b64encode(audio_bytes).decode("ascii")
