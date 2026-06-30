"""
Tool-call router.

For Phase 1, tools are stubbed — we receive the tool call from the LLM
and return a "this is a placeholder" response. Phase 2 (or Phase 1.5)
will forward tool calls to OpenClaw's existing tool-use layer.

DECISIONS.md D6: tool calls go through OpenClaw, not directly to MCP.
This module is where that wiring will land.
"""

from __future__ import annotations

import logging
from typing import Any
import httpx
from .config import settings

log = logging.getLogger(__name__)


async def call_tool(name: str, args: dict[str, Any], call_id: str) -> dict[str, Any]:
    """
    Dispatch a tool call from the LLM.

    Phase 1: stub — return a placeholder response.
    Phase 2: forward to OpenClaw gateway at $OPENCLAW_GATEWAY_URL.

    Returns a dict shaped to fit inside a Gemini Bidi `toolResponse` message.
    """
    log.info("Tool call: %s(%s) [id=%s]", name, args, call_id)

    # TODO(phase-2): forward to OpenClaw
    # async with httpx.AsyncClient(timeout=30) as client:
    #     resp = await client.post(
    #         f"{settings.openclaw_gateway_url}/v1/tools/call",
    #         json={"name": name, "arguments": args},
    #     )
    #     return resp.json()

    return {
        "functionResponses": [
            {
                "id": call_id,
                "name": name,
                "response": {
                    "result": f"[bridge stub] {name} called with {args} — OpenClaw tool wiring is Phase 2"
                },
            }
        ]
    }
