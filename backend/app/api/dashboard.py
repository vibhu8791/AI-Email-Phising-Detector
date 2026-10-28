import os
import sys
from fastapi import APIRouter, Depends

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.connection import db_service
from app.api.websocket import manager
from app.api.auth import get_current_user, UserSession

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: UserSession = Depends(get_current_user)):
    """Retrieve aggregate statistics strictly scoped to authenticated user."""
    stats = await db_service.get_stats(user_id=current_user.user_id)
    return stats

@router.get("/threats")
@router.get("/threats/recent")
async def get_recent_threats(limit: int = 10, current_user: UserSession = Depends(get_current_user)):
    """Retrieve the most recent threat alerts isolated for authenticated user."""
    threats = await db_service.get_recent_threats(user_id=current_user.user_id, limit=limit)
    return threats

@router.post("/reset")
async def reset_dashboard_data(current_user: UserSession = Depends(get_current_user)):
    """Clear scanned emails and threats for the calling user only (preserves other users)."""
    await db_service.clear_user_data(user_id=current_user.user_id)
    await manager.broadcast({"type": "STATS_UPDATED", "user_id": current_user.user_id})
    return {"status": "success", "message": f"Dashboard data cleared for user {current_user.user_id}."}

