import asyncio
import json
import logging
import os
from typing import Iterable, AsyncIterator, Callable, Optional

import websockets

from mcp_core.models import PublicEventLog

REALTIME_WS_URL = "wss://api.openai.com/v1/realtime"
logger = logging.getLogger(__name__)


def log_realtime_event(actor: str, event_type: str, details: str = "") -> None:
    """Persist a realtime token event using PublicEventLog."""
    PublicEventLog.objects.create(
        actor_name=actor,
        event_details=f"{event_type}: {details}",
        success=True,
    )


async def stream_chat(
    messages: Iterable[dict],
    *,
    model: str = "gpt-4o",
    on_event: Optional[Callable[[dict], None]] = None,
) -> AsyncIterator[str]:
    """Yield tokens from the OpenAI Realtime API."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"type": "start", "data": {"model": model, "messages": list(messages)}}

    async with websockets.connect(REALTIME_WS_URL, extra_headers=headers) as ws:
        await ws.send(json.dumps(payload))
        log_realtime_event("assistant", "start")

        try:
            async for raw in ws:
                data = json.loads(raw)
                if on_event:
                    on_event(data)
                if data.get("type") == "token":
                    yield data.get("data", "")
                elif data.get("type") == "edit":
                    log_realtime_event("assistant", "edit")
        finally:
            await ws.send(json.dumps({"type": "stop"}))
            log_realtime_event("assistant", "stop")
