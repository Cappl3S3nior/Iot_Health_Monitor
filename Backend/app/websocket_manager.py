import json
from typing import List

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] client connected. total={len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] client disconnected. total={len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        print(f"[WS] broadcasting to {len(self.active_connections)} clients")
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_text(json.dumps(data, default=str))
                print("[WS] sent:", data.get("type"))
            except Exception:
                print("[WS] broadcast failed:", e)
                dead.append(conn)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()
