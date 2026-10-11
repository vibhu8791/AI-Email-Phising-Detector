import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.connection import db_service
from app.services.analyzer import analyzer
from app.services.gmail_service import gmail_service
from app.api.websocket import manager
from app.core.security import decrypt_token

logger = logging.getLogger("app.emails")
router = APIRouter(prefix="/emails", tags=["Emails & Analysis"])

class CustomEmailAnalysisRequest(BaseModel):
    subject: str
    sender: str
    body: str
    save_result: bool = False

@router.post("/sync")
async def sync_emails(max_count: int = Query(10, ge=1, le=50)):
    """
    Automatically fetch recent emails from connected Gmail account,
    run ML and heuristic phishing analysis, persist results,
    and broadcast real-time threat alerts via WebSockets.
    """
    token_data = await db_service.get_user_tokens()
    if not token_data:
        raise HTTPException(status_code=400, detail="No Gmail account connected. Please connect Gmail or use Demo Mode first.")

    raw_emails = []
    mode = token_data.get("mode", "live")
    if mode == "live":
        try:
            from app.core.security import decrypt_token
            access_token = decrypt_token(token_data.get("access_token_encrypted", ""))
            refresh_token = decrypt_token(token_data.get("refresh_token_encrypted", ""))
            raw_emails = gmail_service.fetch_live_emails(access_token, refresh_token, max_results=max_count)
        except Exception as e:
            logger.error(f"Failed to fetch live Gmail emails: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch real emails from Google: {e}")
    else:
        raise HTTPException(status_code=400, detail="Demo mode is disabled. Please connect a real Google account.")

    scanned_records = []
    threat_count = 0

    for raw in raw_emails:
        # Run Phishing Detection Engine
        analysis = analyzer.analyze(
            subject=raw.get("subject", ""),
            sender=raw.get("sender", ""),
            body=raw.get("body_plain", "") or raw.get("snippet", ""),
            recipient=raw.get("recipient")
        )

        email_record = {
            "id": raw.get("id") or str(uuid.uuid4()),
            "message_id": raw.get("message_id"),
            "subject": raw.get("subject", "(No Subject)"),
            "sender": raw.get("sender", "Unknown"),
            "recipient": raw.get("recipient"),
            "date": raw.get("date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            "snippet": raw.get("snippet", ""),
            "body_plain": raw.get("body_plain", ""),
            "body_html": raw.get("body_html"),
            "extracted_urls": analysis["extracted_urls"],
            "ml_phishing_probability": analysis["ml_phishing_probability"],
            "heuristic_score": analysis["heuristic_score"],
            "risk_score": analysis["risk_score"],
            "classification": analysis["classification"],
            "detected_flags": analysis["detected_flags"],
            "keyword_matches": analysis["keyword_matches"],
            "url_details": analysis["url_details"],
            "created_at": datetime.utcnow().isoformat()
        }

        # Save to Database
        await db_service.save_email(email_record)
        scanned_records.append(email_record)

        # If Phishing or Suspicious, trigger real-time broadcast and log threat
        if email_record["classification"] in ["PHISHING", "SUSPICIOUS"]:
            threat_count += 1
            threat_entry = {
                "id": str(uuid.uuid4()),
                "email_id": email_record["id"],
                "subject": email_record["subject"],
                "sender": email_record["sender"],
                "risk_score": email_record["risk_score"],
                "classification": email_record["classification"],
                "reasons": email_record["detected_flags"],
                "timestamp": datetime.utcnow().isoformat()
            }
            await db_service.save_threat(threat_entry)
            # Push WebSocket alert to all active dashboard connections
            await manager.broadcast_alert(email_record)

    # Update last sync timestamp
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await db_service.update_last_sync(token_data.get("email", ""), now_str)

    # Also broadcast stats refresh event
    await manager.broadcast({"type": "STATS_UPDATED"})

    return {
        "status": "success",
        "scanned_count": len(scanned_records),
        "threats_detected": threat_count,
        "last_synced_at": now_str,
        "items": scanned_records
    }

@router.get("")
async def get_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    classification: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Retrieve scanned emails with search and classification filter."""
    result = await db_service.get_emails(skip=skip, limit=limit, classification=classification, search=search)
    return result

@router.get("/{email_id}")
async def get_email_details(email_id: str):
    """Retrieve in-depth details of a specific scanned email."""
    email_doc = await db_service.get_email_by_id(email_id)
    if not email_doc:
        raise HTTPException(status_code=404, detail="Email record not found.")
    return email_doc

@router.delete("/{email_id}")
async def delete_email(email_id: str):
    """Delete a scanned email record."""
    success = await db_service.delete_email(email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found.")
    await manager.broadcast({"type": "STATS_UPDATED"})
    return {"status": "success", "message": "Email deleted successfully."}

@router.post("/analyze-custom")
async def analyze_custom_email(req: CustomEmailAnalysisRequest):
    """
    On-demand interactive sandbox:
    Analyze any arbitrary email subject, sender, and body using the AI/ML model.
    """
    analysis = analyzer.analyze(
        subject=req.subject,
        sender=req.sender,
        body=req.body
    )

    record = {
        "id": str(uuid.uuid4()),
        "subject": req.subject,
        "sender": req.sender,
        "body_plain": req.body,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        **analysis,
        "created_at": datetime.utcnow().isoformat()
    }

    if req.save_result:
        await db_service.save_email(record)
        if record["classification"] in ["PHISHING", "SUSPICIOUS"]:
            await db_service.save_threat({
                "id": str(uuid.uuid4()),
                "email_id": record["id"],
                "subject": record["subject"],
                "sender": record["sender"],
                "risk_score": record["risk_score"],
                "classification": record["classification"],
                "reasons": record["detected_flags"],
                "timestamp": datetime.utcnow().isoformat()
            })
            await manager.broadcast_alert(record)
        await manager.broadcast({"type": "STATS_UPDATED"})

    return record

@router.post("/simulate-batch")
async def simulate_batch():
    """
    One-click quick seed:
    Simulates scanning a batch of realistic emails to immediately demonstrate
    real-time alerts, risk scoring, and dashboard graphs.
    """
    demo_emails = gmail_service.get_sample_demo_emails()
    results = []

    for raw in demo_emails:
        analysis = analyzer.analyze(
            subject=raw.get("subject", ""),
            sender=raw.get("sender", ""),
            body=raw.get("body_plain", "")
        )

        rec = {
            "id": raw.get("id") or str(uuid.uuid4()),
            "message_id": raw.get("message_id"),
            "subject": raw.get("subject"),
            "sender": raw.get("sender"),
            "recipient": raw.get("recipient"),
            "date": raw.get("date"),
            "snippet": raw.get("snippet"),
            "body_plain": raw.get("body_plain"),
            "body_html": raw.get("body_html"),
            "extracted_urls": analysis["extracted_urls"],
            "ml_phishing_probability": analysis["ml_phishing_probability"],
            "heuristic_score": analysis["heuristic_score"],
            "risk_score": analysis["risk_score"],
            "classification": analysis["classification"],
            "detected_flags": analysis["detected_flags"],
            "keyword_matches": analysis["keyword_matches"],
            "url_details": analysis["url_details"],
            "created_at": datetime.utcnow().isoformat()
        }
        await db_service.save_email(rec)
        results.append(rec)

        if rec["classification"] in ["PHISHING", "SUSPICIOUS"]:
            await db_service.save_threat({
                "id": str(uuid.uuid4()),
                "email_id": rec["id"],
                "subject": rec["subject"],
                "sender": rec["sender"],
                "risk_score": rec["risk_score"],
                "classification": rec["classification"],
                "reasons": rec["detected_flags"],
                "timestamp": datetime.utcnow().isoformat()
            })
            await manager.broadcast_alert(rec)

    await manager.broadcast({"type": "STATS_UPDATED"})
    return {
        "status": "success",
        "message": f"Successfully simulated and analyzed {len(results)} sample emails.",
        "count": len(results)
    }
