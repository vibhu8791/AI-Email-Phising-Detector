import os
import sys
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.connection import db_service
from app.services.analyzer import analyzer
from app.services.gmail_service import gmail_service, GmailAuthRevokedError
from app.api.websocket import manager
from app.api.auth import get_current_user, UserSession
from app.core.security import decrypt_token

logger = logging.getLogger("app.emails")
router = APIRouter(prefix="/emails", tags=["Emails & Analysis"])

class CustomEmailAnalysisRequest(BaseModel):
    subject: str
    sender: str
    body: str
    save_result: bool = False

@router.post("/sync")
async def sync_emails(
    max_count: int = Query(10, ge=1, le=50),
    account_id: Optional[str] = Query(None),
    current_user: UserSession = Depends(get_current_user)
):
    """
    Fetch recent emails from the selected connected Gmail account,
    run ML and heuristic phishing analysis using the production analyzer,
    persist results isolated under current_user, and broadcast real-time threat alerts.
    """
    account = await db_service.get_account(user_id=current_user.user_id, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=400, 
            detail="No connected Gmail account found for this user. Please connect Gmail or use Demo Mode first."
        )

    if account.get("status") in ("revoked", "expired"):
        raise HTTPException(
            status_code=401,
            detail="Gmail account authorization has expired or was revoked. Please reconnect this account."
        )

    raw_emails = []
    mode = account.get("mode", "live")
    account_email = account.get("email", "unknown@gmail.com")
    acc_id = account.get("id")

    if mode == "live":
        try:
            access_token = decrypt_token(account.get("access_token_encrypted", ""))
            refresh_token = decrypt_token(account.get("refresh_token_encrypted", "")) if account.get("refresh_token_encrypted") else None
            raw_emails = gmail_service.fetch_live_emails(access_token, refresh_token, max_results=max_count)
        except GmailAuthRevokedError as re:
            logger.warning(f"Gmail token revoked for {account_email}: {re}")
            await db_service.update_account_status(
                user_id=current_user.user_id,
                account_id=acc_id,
                status="revoked",
                error_message="Authorization revoked or expired by Google"
            )
            raise HTTPException(status_code=401, detail="Google OAuth token has been revoked or expired. Please re-authorize this account.")
        except Exception as e:
            logger.error(f"Failed to fetch live Gmail emails for {account_email}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch emails from Google: {e}")
    elif mode == "demo":
        raw_emails = gmail_service.get_sample_demo_emails()[:max_count]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown account mode: {mode}")

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
            "id": str(uuid.uuid4()),
            "message_id": raw.get("message_id") or raw.get("id"),
            "user_id": current_user.user_id,
            "account_id": acc_id,
            "account_email": account_email,
            "subject": raw.get("subject", "(No Subject)"),
            "sender": raw.get("sender", "Unknown"),
            "recipient": raw.get("recipient"),
            "date": raw.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
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
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Save to Database strictly isolated under user_id
        await db_service.save_email(email_record, user_id=current_user.user_id)
        scanned_records.append(email_record)

        # If Phishing or Suspicious, trigger real-time broadcast and log threat
        if email_record["classification"] in ["PHISHING", "SUSPICIOUS"]:
            threat_count += 1
            threat_entry = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.user_id,
                "account_id": acc_id,
                "account_email": account_email,
                "email_id": email_record["id"],
                "subject": email_record["subject"],
                "sender": email_record["sender"],
                "risk_score": email_record["risk_score"],
                "classification": email_record["classification"],
                "reasons": email_record["detected_flags"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db_service.save_threat(threat_entry, user_id=current_user.user_id)
            # Push WebSocket alert to all active dashboard connections
            await manager.broadcast_alert(email_record)

    # Update last sync timestamp for this account
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    await db_service.update_last_sync(account_email, now_str)

    # Also broadcast stats refresh event
    await manager.broadcast({"type": "STATS_UPDATED", "user_id": current_user.user_id})

    return {
        "status": "success",
        "account_id": acc_id,
        "account_email": account_email,
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
    search: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    current_user: UserSession = Depends(get_current_user)
):
    """Retrieve scanned emails strictly scoped to authenticated user and optional account."""
    result = await db_service.get_emails(
        user_id=current_user.user_id,
        account_id=account_id,
        skip=skip,
        limit=limit,
        classification=classification,
        search=search
    )
    return result

@router.get("/{email_id}")
async def get_email_details(
    email_id: str,
    current_user: UserSession = Depends(get_current_user)
):
    """Retrieve in-depth details of a specific scanned email owned by user."""
    email_doc = await db_service.get_email_by_id(email_id, user_id=current_user.user_id)
    if not email_doc:
        raise HTTPException(status_code=404, detail="Email record not found or access denied.")
    return email_doc

@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    current_user: UserSession = Depends(get_current_user)
):
    """Delete a scanned email record owned by user."""
    success = await db_service.delete_email(email_id, user_id=current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found or access denied.")
    await manager.broadcast({"type": "STATS_UPDATED", "user_id": current_user.user_id})
    return {"status": "success", "message": "Email deleted successfully."}

@router.post("/analyze-custom")
async def analyze_custom_email(
    req: CustomEmailAnalysisRequest,
    current_user: UserSession = Depends(get_current_user)
):
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
        "user_id": current_user.user_id,
        "subject": req.subject,
        "sender": req.sender,
        "body_plain": req.body,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        **analysis,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if req.save_result:
        await db_service.save_email(record, user_id=current_user.user_id)
        if record["classification"] in ["PHISHING", "SUSPICIOUS"]:
            await db_service.save_threat({
                "id": str(uuid.uuid4()),
                "user_id": current_user.user_id,
                "email_id": record["id"],
                "subject": record["subject"],
                "sender": record["sender"],
                "risk_score": record["risk_score"],
                "classification": record["classification"],
                "reasons": record["detected_flags"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, user_id=current_user.user_id)
            await manager.broadcast_alert(record)
        await manager.broadcast({"type": "STATS_UPDATED", "user_id": current_user.user_id})

    return record

@router.post("/simulate-batch")
async def simulate_batch(
    account_id: Optional[str] = Query(None),
    current_user: UserSession = Depends(get_current_user)
):
    """
    Simulates scanning a batch of realistic emails isolated under current_user.
    """
    account = await db_service.get_account(user_id=current_user.user_id, account_id=account_id)
    acc_id = account.get("id") if account else None
    acc_email = account.get("email") if account else "demo.mailbox@local"

    demo_emails = gmail_service.get_sample_demo_emails()
    results = []

    for raw in demo_emails:
        analysis = analyzer.analyze(
            subject=raw.get("subject", ""),
            sender=raw.get("sender", ""),
            body=raw.get("body_plain", "")
        )

        rec = {
            "id": str(uuid.uuid4()),
            "message_id": raw.get("message_id") or raw.get("id"),
            "user_id": current_user.user_id,
            "account_id": acc_id,
            "account_email": acc_email,
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
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db_service.save_email(rec, user_id=current_user.user_id)
        results.append(rec)

        if rec["classification"] in ["PHISHING", "SUSPICIOUS"]:
            await db_service.save_threat({
                "id": str(uuid.uuid4()),
                "user_id": current_user.user_id,
                "account_id": acc_id,
                "account_email": acc_email,
                "email_id": rec["id"],
                "subject": rec["subject"],
                "sender": rec["sender"],
                "risk_score": rec["risk_score"],
                "classification": rec["classification"],
                "reasons": rec["detected_flags"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, user_id=current_user.user_id)
            await manager.broadcast_alert(rec)

    await manager.broadcast({"type": "STATS_UPDATED", "user_id": current_user.user_id})
    return {
        "status": "success",
        "message": f"Successfully simulated and analyzed {len(results)} sample emails.",
        "count": len(results)
    }

