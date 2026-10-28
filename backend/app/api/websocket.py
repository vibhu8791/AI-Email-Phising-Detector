import json
import logging
from typing import List, Dict, Optional, Tuple
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("app.websocket")

class ConnectionManager:
    def __init__(self):
        # List of (websocket, user_id) tuples
        self.active_connections: List[Tuple[WebSocket, Optional[str]]] = []

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append((websocket, user_id))
        logger.info(f"WebSocket client connected (user: {user_id or 'anonymous'}). Total active: {len(self.active_connections)}")
        # Send welcome ack
        await websocket.send_json({
            "type": "SYSTEM_CONNECTED",
            "message": "Connected to real-time Phishing Threat Alert Stream",
            "user_id": user_id
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [
            conn for conn in self.active_connections if conn[0] != websocket
        ]
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, data: dict, user_id: Optional[str] = None):
        """Broadcast event to dashboard frontends, scoped to user_id if specified."""
        dead_connections = []
        for ws, conn_user in self.active_connections:
            # If user_id is specified, only deliver to matching user or legacy/global listeners
            if user_id and conn_user and conn_user != user_id:
                continue
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.append(ws)

        for dead in dead_connections:
            self.disconnect(dead)

    async def broadcast_alert(self, email_record: dict, user_id: Optional[str] = None):
        """High-priority broadcast when Phishing or Suspicious email is detected."""
        payload = {
            "type": "PHISHING_ALERT",
            "user_id": user_id or email_record.get("user_id"),
            "email_id": email_record.get("id"),
            "subject": email_record.get("subject"),
            "sender": email_record.get("sender"),
            "risk_score": email_record.get("risk_score"),
            "classification": email_record.get("classification"),
            "detected_flags": email_record.get("detected_flags", []),
            "timestamp": email_record.get("created_at") or email_record.get("date")
        }
        await self.broadcast(payload, user_id=user_id or email_record.get("user_id"))

manager = ConnectionManager()
