import json
import logging
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("app.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")
        # Send welcome ack
        await websocket.send_json({
            "type": "SYSTEM_CONNECTED",
            "message": "Connected to real-time Phishing Threat Alert Stream"
        })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """Broadcast event to all connected dashboard frontends."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    async def broadcast_alert(self, email_record: dict):
        """High-priority broadcast when Phishing or Suspicious email is detected."""
        payload = {
            "type": "PHISHING_ALERT",
            "email_id": email_record.get("id"),
            "subject": email_record.get("subject"),
            "sender": email_record.get("sender"),
            "risk_score": email_record.get("risk_score"),
            "classification": email_record.get("classification"),
            "detected_flags": email_record.get("detected_flags", []),
            "timestamp": email_record.get("created_at") or email_record.get("date")
        }
        await self.broadcast(payload)

manager = ConnectionManager()
