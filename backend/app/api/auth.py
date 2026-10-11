import os
import sys
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
import requests
from typing import Optional

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.core.security import encrypt_token, decrypt_token
from database.connection import db_service

logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/auth", tags=["Google OAuth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly"
]

@router.get("/google/login")
async def google_login():
    """Redirect directly to Google OAuth 2.0 consent screen."""
    logger.info(f"DEBUG LOGIN HIT. CLIENT ID IS: {settings.GOOGLE_CLIENT_ID}")
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID":
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error=MissingClientID")

    scope_str = "%20".join(SCOPES)
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scope_str}&"
        f"access_type=offline&"
        f"prompt=select_account"
    )
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_oauth_callback(code: Optional[str] = Query(None), error: Optional[str] = Query(None)):
    """Handle authorization code returned from Google OAuth 2.0 consent screen."""
    if error:
        logger.error(f"Google OAuth error returned: {error}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    try:
        # Exchange code for tokens
        token_payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        res = requests.post(GOOGLE_TOKEN_URL, data=token_payload, timeout=10)
        tokens = res.json()

        if "error" in tokens:
            logger.error(f"Token exchange error: {tokens}")
            return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error={tokens.get('error_description', tokens.get('error'))}")

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")

        # Fetch authenticated user profile
        user_info_res = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        user_info = user_info_res.json()
        user_email = user_info.get("email", "user@gmail.com")

        # Encrypt tokens before saving
        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

        await db_service.save_user_tokens({
            "email": user_email,
            "access_token_encrypted": encrypted_access,
            "refresh_token_encrypted": encrypted_refresh,
            "expires_in": expires_in,
            "connected_at": datetime.utcnow().isoformat(),
            "last_synced_at": None,
            "mode": "live"
        })

        logger.info(f"Successfully connected Gmail for {user_email}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth=success&email={user_email}")

    except Exception as e:
        logger.error(f"Exception during OAuth callback: {e}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error=InternalServerError")

@router.get("/status")
async def get_connection_status():
    """Retrieve current Gmail connection status."""
    token_data = await db_service.get_user_tokens()
    if token_data and token_data.get("email"):
        return {
            "is_connected": True,
            "email": token_data.get("email"),
            "mode": token_data.get("mode", "live"),
            "last_synced_at": token_data.get("last_synced_at"),
            "connected_at": token_data.get("connected_at")
        }
    return {
        "is_connected": False,
        "email": None,
        "mode": None,
        "last_synced_at": None
    }

@router.post("/disconnect")
async def disconnect_gmail():
    """Disconnect Gmail account and clear stored OAuth tokens."""
    await db_service.clear_user_tokens()
    return {"status": "success", "message": "Gmail account disconnected successfully."}

@router.post("/demo-connect")
async def connect_demo_mailbox():
    """Connect a simulated demo Gmail account for zero-configuration testing."""
    demo_email = "demo.analyst@gmail.com"
    await db_service.save_user_tokens({
        "email": demo_email,
        "access_token_encrypted": encrypt_token("demo_token"),
        "refresh_token_encrypted": encrypt_token("demo_refresh_token"),
        "connected_at": datetime.utcnow().isoformat(),
        "last_synced_at": None,
        "mode": "demo"
    })
    return {
        "status": "success",
        "email": demo_email,
        "mode": "demo",
        "message": "Connected to Demo Gmail Mailbox"
    }
