import os
import sys
from fastapi import APIRouter

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.connection import db_service
from app.api.websocket import manager

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats():
    """Retrieve aggregate statistics for the dashboard overview."""
    stats = await db_service.get_stats()
    return stats

@router.get("/threats/recent")
async def get_recent_threats(limit: int = 10):
    """Retrieve the most recent threat alerts."""
    threats = await db_service.get_recent_threats(limit=limit)
    return threats

@router.post("/reset")
async def reset_dashboard_data():
    """Clear all scanned emails and threats for clean testing."""
    if not db_service.use_fallback and db_service.db is not None:
        try:
            await db_service.db.scanned_emails.delete_many({})
            await db_service.db.threat_logs.delete_many({})
        except Exception:
            pass
    db_service._memory_data["scanned_emails"] = []
    db_service._memory_data["threat_logs"] = []
    db_service._persist_fallback()
    await manager.broadcast({"type": "STATS_UPDATED"})
    return {"status": "success", "message": "Dashboard data cleared."}
