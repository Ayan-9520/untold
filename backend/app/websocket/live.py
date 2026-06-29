"""WebSocket — real-time live scores, events, and commentary."""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.live_cache import LIVE_CHANNEL

logger = logging.getLogger("untold")
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "live"):
        await websocket.accept()
        self.active.setdefault(channel, []).append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "live"):
        if channel in self.active and websocket in self.active[channel]:
            self.active[channel].remove(websocket)

    async def broadcast(self, message: dict, channel: str = "live"):
        dead = []
        for ws in self.active.get(channel, []):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, channel)


manager = ConnectionManager()


@router.websocket("/ws/live")
async def live_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "connected", "channel": "live"})
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.startswith("subscribe:"):
                match_id = data.split(":", 1)[1]
                await websocket.send_json({"type": "subscribed", "match_id": match_id})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_live_update(payload: dict):
    await manager.broadcast({"type": "live_update", "data": payload})


async def redis_live_listener():
    """Subscribe to Redis pub/sub and push updates to WebSocket clients."""
    try:
        import redis

        from app.core.config import get_settings

        settings = get_settings()
        client = redis.from_url(settings.redis_url, decode_responses=True)
        pubsub = client.pubsub()
        pubsub.subscribe(LIVE_CHANNEL)
        logger.info("WebSocket Redis listener started on %s", LIVE_CHANNEL)

        while True:
            message = await asyncio.to_thread(
                pubsub.get_message, ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message.get("type") == "message":
                try:
                    payload = json.loads(message["data"])
                    await broadcast_live_update(payload)
                except (json.JSONDecodeError, TypeError) as exc:
                    logger.warning("Invalid live pub/sub payload: %s", exc)
            await asyncio.sleep(0.05)
    except Exception as exc:
        logger.warning("Redis live listener unavailable: %s", exc)
