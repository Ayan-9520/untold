"""UNTOLD Studio realtime notifications WebSocket."""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.core.session_security import validate_token_session
from app.db.session import SessionLocal
from app.domain.collaboration.helpers import room_key
from app.models import User

logger = logging.getLogger("untold.studio.ws")
router = APIRouter()


class StudioConnectionManager:
    def __init__(self) -> None:
        self.active: dict[int, list[WebSocket]] = {}
        self.rooms: dict[str, set[tuple[int, WebSocket]]] = {}
        self.ws_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        conns = self.active.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self.active.pop(user_id, None)

        for room in list(self.ws_rooms.get(websocket, set())):
            self.leave_room(room, user_id, websocket)
        self.ws_rooms.pop(websocket, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        for ws in self.active.get(user_id, []):
            try:
                await ws.send_json(payload)
            except Exception:
                logger.debug("Failed to push studio WS message to user %s", user_id)

    def join_room(self, room: str, user_id: int, websocket: WebSocket) -> None:
        self.rooms.setdefault(room, set()).add((user_id, websocket))
        self.ws_rooms.setdefault(websocket, set()).add(room)

    def leave_room(self, room: str, user_id: int, websocket: WebSocket) -> None:
        members = self.rooms.get(room, set())
        members.discard((user_id, websocket))
        if not members:
            self.rooms.pop(room, None)
        ws_set = self.ws_rooms.get(websocket, set())
        ws_set.discard(room)

    async def broadcast_room(self, room: str, payload: dict, *, exclude: WebSocket | None = None) -> None:
        for _uid, ws in list(self.rooms.get(room, set())):
            if exclude and ws is exclude:
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                logger.debug("Failed to broadcast to room %s", room)


manager = StudioConnectionManager()


def _authenticate_ws(token: str | None) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = int(payload["sub"])
    except Exception:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if not user:
            return None
        if not user.is_admin and not user.studio_role:
            return None
        validate_token_session(db, payload)
        return user
    except Exception:
        return None
    finally:
        db.close()


def _user_can_access_project(user: User, project_id: int) -> bool:
    db = SessionLocal()
    try:
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        return True
    except Exception:
        return False
    finally:
        db.close()


@router.websocket("/ws/studio")
async def studio_notifications_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = _authenticate_ws(token)
    if not user:
        await websocket.close(code=4401)
        return

    await manager.connect(user.id, websocket)
    try:
        await websocket.send_json({"type": "connected", "user_id": user.id})
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "join_room":
                project_id = msg.get("project_id")
                if project_id and _user_can_access_project(user, int(project_id)):
                    rtype = msg.get("resource_type", "project")
                    rid = msg.get("resource_id")
                    room = room_key(int(project_id), rtype, int(rid) if rid is not None else None)
                    manager.join_room(room, user.id, websocket)
                    await websocket.send_json({"type": "joined_room", "room": room})
                elif project_id:
                    await websocket.send_json({"type": "error", "detail": "Project access denied"})
                continue

            if msg_type == "leave_room":
                room = msg.get("room")
                if room:
                    manager.leave_room(room, user.id, websocket)
                continue

            if msg_type == "collab_patch":
                project_id = msg.get("project_id")
                if project_id and _user_can_access_project(user, int(project_id)):
                    room = room_key(
                        int(project_id),
                        msg.get("resource_type", "document"),
                        msg.get("resource_id"),
                    )
                    await manager.broadcast_room(
                        room,
                        {
                            "type": "collaboration_event",
                            "event": "live_patch",
                            "user_id": user.id,
                            "name": user.full_name,
                            **{k: v for k, v in msg.items() if k != "type"},
                        },
                        exclude=websocket,
                    )
                continue

    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
