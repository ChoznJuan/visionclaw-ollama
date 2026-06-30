"""
Protocol models for the Gemini BidiGenerateContent WebSocket protocol.

This is the protocol the upstream VisionClaw Android sample uses (see
samples/CameraAccessAndroid/.../gemini/GeminiLiveService.kt). Our bridge
speaks this protocol on the wire so the Android client doesn't need
modification — we just translate internally to Ollama + Speaches.

Reference: Google's Gemini Live API docs (BidiGenerateContent).
The exact field names are taken verbatim from the upstream client source.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ====== Client → Server ======

class SetupMessage(BaseModel):
    """Initial message after WebSocket open. Matches upstream's sendSetupMessage()."""
    model: str
    generation_config: dict[str, Any] = Field(alias="generationConfig")
    system_instruction: dict[str, Any] | None = Field(None, alias="systemInstruction")
    tools: list[dict[str, Any]] | None = None
    realtime_input_config: dict[str, Any] | None = Field(None, alias="realtimeInputConfig")
    context_window_compression: dict[str, Any] | None = Field(None, alias="contextWindowCompression")
    input_audio_transcription: dict[str, Any] | None = Field(None, alias="inputAudioTranscription")
    output_audio_transcription: dict[str, Any] | None = Field(None, alias="outputAudioTranscription")

    model_config = {"populate_by_name": True}


class RealtimeInputAudio(BaseModel):
    """Audio chunk from the client. PCM 16kHz mono 16-bit, base64-encoded."""
    mimeType: str = "audio/pcm;rate=16000"
    data: str  # base64


class RealtimeInputVideo(BaseModel):
    """Video frame from the client. JPEG, base64-encoded."""
    mimeType: str = "image/jpeg"
    data: str  # base64


class RealtimeInput(BaseModel):
    audio: RealtimeInputAudio | None = None
    video: RealtimeInputVideo | None = None


class ClientContentTurnPart(BaseModel):
    text: str | None = None
    inline_data: dict[str, Any] | None = Field(None, alias="inlineData")

    model_config = {"populate_by_name": True}


class ClientContentTurn(BaseModel):
    role: str  # "user" or "model"
    parts: list[ClientContentTurnPart]


class ClientContent(BaseModel):
    turns: list[ClientContentTurn]
    turn_complete: bool | None = Field(None, alias="turnComplete")

    model_config = {"populate_by_name": True}


# ====== Server → Client ======

class SetupComplete(BaseModel):
    """Sent once after the client setup message is accepted."""
    pass


class ServerContentModelTurnPart(BaseModel):
    inline_data: dict[str, Any] | None = Field(None, alias="inlineData")
    text: str | None = None

    model_config = {"populate_by_name": True}


class ServerContentModelTurn(BaseModel):
    parts: list[ServerContentModelTurnPart]


class ServerContent(BaseModel):
    model_turn: ServerContentModelTurn | None = Field(None, alias="modelTurn")
    turn_complete: bool | None = Field(None, alias="turnComplete")
    interrupted: bool | None = None
    input_transcription: dict[str, Any] | None = Field(None, alias="inputTranscription")
    output_transcription: dict[str, Any] | None = Field(None, alias="outputTranscription")

    model_config = {"populate_by_name": True}


class ToolCallFunctionCall(BaseModel):
    name: str
    args: dict[str, Any]
    id: str | None = None


class ToolCall(BaseModel):
    function_calls: list[ToolCallFunctionCall] = Field(alias="functionCalls")
    model_config = {"populate_by_name": True}


class ToolCallCancellation(BaseModel):
    ids: list[str]


# ====== Helpers for raw dicts (the protocol uses loose JSON; pydantic is just for docs) ======

def is_setup_message(msg: dict) -> bool:
    return "setup" in msg


def is_setup_complete(msg: dict) -> bool:
    return "setupComplete" in msg


def is_realtime_input(msg: dict) -> bool:
    return "realtimeInput" in msg


def is_client_content(msg: dict) -> bool:
    return "clientContent" in msg


def is_tool_response(msg: dict) -> bool:
    return "toolResponse" in msg


def is_server_content(msg: dict) -> bool:
    return "serverContent" in msg


def is_tool_call(msg: dict) -> bool:
    return "toolCall" in msg
