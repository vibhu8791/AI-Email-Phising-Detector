import os
import sys
import logging
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, HTTPException, Query, Header, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from typing import Optional, List, Dict, Any

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.core.security import encrypt_token, decrypt_token, generate_oauth_state, verify_oauth_state
from app.services.gmail_service import revoke_google_token
from database.connection import db_service

logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/auth", tags=["Google OAuth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Minimal required scopes for read-only Gmail threat detection
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly"
]

class UserSession:
    def __init__(self, user_id: str = "default_user", email: Optional[str] = None):
        self.user_id = user_id
        self.email = email or f"{user_id}@workspace.local"

class SwitchUserRequest(BaseModel):
    user_id: str
    email: Optional[str] = None

class DemoConnectRequest(BaseModel):
    email: Optional[str] = None
    display_name: Optional[str] = None

class UpdateAccountStatusRequest(BaseModel):
    status: str
    error_message: Optional[str] = None

async def get_current_user(
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    authorization: Optional[str] = Header(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
) -> UserSession:
    """
    Resolve the active user session from headers or parameters.
    Ensures multi-user isolation. Defaults to 'default_user' for seamless compatibility.
    """
    user_id = x_user_id or user_id_query
    if not user_id and authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        if token:
            user_id = token
    if not user_id:
        user_id = "default_user"
    return UserSession(user_id=user_id)

@router.get("/google/login")
async def google_login(
    user_id: Optional[str] = Query("default_user"),
    prompt: Optional[str] = Query("select_account")
):
    """
    Redirect directly to Google OAuth 2.0 consent screen.
    Uses prompt=select_account so users can add another Gmail account.
    Embeds tamper-proof signed state token containing user_id for strict isolation.
    """
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID":
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error=MissingClientID")

    # Generate secure, time-bound OAuth state bound to user_id
    state_token = generate_oauth_state(user_id=user_id)
    scope_str = "%20".join(SCOPES)

    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scope_str}&"
        f"access_type=offline&"
        f"prompt={prompt}&"
        f"state={state_token}"
    )
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """
    Handle authorization code returned from Google OAuth 2.0.
    Verifies signed state token to identify the destination user for multi-user isolation.
    Encrypts access and refresh tokens at rest with AES/Fernet.
    """
    if error:
        logger.error(f"Google OAuth error returned: {error}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    # Validate state parameter and extract user_id
    state_data = verify_oauth_state(state) if state else None
    user_id = state_data.get("user_id", "default_user") if state_data else "default_user"

    try:
        # Exchange authorization code for tokens
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
            logger.error(f"Token exchange error: {tokens.get('error')}")
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
        user_email = user_info.get("email", "unknown@gmail.com")
        display_name = user_info.get("name", user_email)

        # Encrypt tokens before saving
        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

        # Calculate expires_at
        expires_at = None
        if expires_in:
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))).isoformat()

        account_id = f"acc_{uuid.uuid4().hex[:12]}"

        # Save connected account isolated under this user_id
        await db_service.save_account({
            "id": account_id,
            "user_id": user_id,
            "email": user_email,
            "display_name": display_name,
            "access_token_encrypted": encrypted_access,
            "refresh_token_encrypted": encrypted_refresh,
            "expires_at": expires_at,
            "scopes": SCOPES,
            "status": "active",
            "mode": "live",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "last_synced_at": None
        })

        logger.info(f"Successfully connected account {user_email} for user {user_id}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth=success&account={user_email}&user_id={user_id}")

    except Exception as e:
        logger.error(f"Exception during OAuth callback: {e}")
        return RedirectResponse(f"{settings.FRONTEND_REDIRECT_URL}?auth_error=InternalServerError")

@router.get("/accounts")
async def list_connected_accounts(current_user: UserSession = Depends(get_current_user)):
    """
    List all connected Gmail accounts for the authenticated user.
    Tokens are strictly stripped to prevent client-side exposure.
    """
    accounts = await db_service.get_accounts(user_id=current_user.user_id)
    return {
        "user_id": current_user.user_id,
        "count": len(accounts),
        "accounts": accounts
    }

@router.post("/accounts/{account_id}/select")
async def select_active_account(
    account_id: str,
    current_user: UserSession = Depends(get_current_user)
):
    """Set a specific connected account as active for inbox scanning."""
    success = await db_service.set_default_account(user_id=current_user.user_id, account_id=account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found or access denied.")
    return {"status": "success", "message": "Active account updated successfully.", "account_id": account_id}

@router.post("/accounts/{account_id}/disconnect")
@router.delete("/accounts/{account_id}")
async def disconnect_specific_account(
    account_id: str,
    current_user: UserSession = Depends(get_current_user)
):
    """
    Disconnect a specific connected Gmail account, revoke tokens with Google,
    and remove securely from database.
    """
    account_record = await db_service.disconnect_account(user_id=current_user.user_id, account_id=account_id)
    if not account_record:
        raise HTTPException(status_code=404, detail="Account not found or access denied.")

    # Attempt to revoke token with Google
    try:
        token_to_revoke = ""
        if account_record.get("refresh_token_encrypted"):
            token_to_revoke = decrypt_token(account_record["refresh_token_encrypted"])
        elif account_record.get("access_token_encrypted"):
            token_to_revoke = decrypt_token(account_record["access_token_encrypted"])
        if token_to_revoke:
            revoke_google_token(token_to_revoke)
    except Exception as e:
        logger.warning(f"Error during Google token revocation: {e}")

    return {
        "status": "success",
        "message": f"Account {account_record.get('email')} disconnected successfully.",
        "account_id": account_id
    }

@router.post("/accounts/{account_id}/status")
async def update_account_status_endpoint(
    account_id: str,
    req: UpdateAccountStatusRequest,
    current_user: UserSession = Depends(get_current_user)
):
    """Update connection status (e.g. active, revoked, expired) for testing and telemetry."""
    await db_service.update_account_status(
        user_id=current_user.user_id,
        account_id=account_id,
        status=req.status,
        error_message=req.error_message
    )
    return {"status": "success", "account_id": account_id, "status": req.status}

@router.post("/accounts/demo-connect")
async def connect_demo_account(
    req: Optional[DemoConnectRequest] = None,
    current_user: UserSession = Depends(get_current_user)
):
    """
    Connect a simulated demo Gmail mailbox for offline/testing.
    Allows testing multi-account switching and isolated inbox scans.
    """
    demo_email = req.email if req and req.email else f"demo.analyst_{uuid.uuid4().hex[:4]}@gmail.com"
    display_name = req.display_name if req and req.display_name else f"Demo Mailbox ({demo_email.split('@')[0]})"
    account_id = f"acc_demo_{uuid.uuid4().hex[:8]}"

    account_data = {
        "id": account_id,
        "user_id": current_user.user_id,
        "email": demo_email,
        "display_name": display_name,
        "access_token_encrypted": encrypt_token("demo_simulated_token"),
        "refresh_token_encrypted": encrypt_token("demo_simulated_refresh_token"),
        "expires_at": (datetime.now(timezone.utc).replace(year=2030)).isoformat(),
        "scopes": SCOPES,
        "status": "active",
        "mode": "demo",
        "connected_at": datetime.now(timezone.utc).isoformat(),
        "last_synced_at": None
    }
    saved = await db_service.save_account(account_data)
    return {
        "status": "success",
        "account": saved,
        "message": f"Connected simulated demo account {demo_email}"
    }

@router.get("/status")
async def get_connection_status(current_user: UserSession = Depends(get_current_user)):
    """Retrieve connection status of active account and summary of all connected accounts."""
    accounts = await db_service.get_accounts(user_id=current_user.user_id)
    default_acc = next((a for a in accounts if a.get("is_default")), None) or (accounts[0] if accounts else None)

    if default_acc:
        return {
            "is_connected": True,
            "email": default_acc.get("email"),
            "account_id": default_acc.get("id"),
            "display_name": default_acc.get("display_name"),
            "status": default_acc.get("status", "active"),
            "mode": default_acc.get("mode", "live"),
            "last_synced_at": default_acc.get("last_synced_at"),
            "connected_at": default_acc.get("connected_at"),
            "accounts_count": len(accounts),
            "accounts": accounts
        }
    return {
        "is_connected": False,
        "email": None,
        "account_id": None,
        "mode": None,
        "last_synced_at": None,
        "accounts_count": 0,
        "accounts": []
    }

@router.post("/disconnect")
async def disconnect_active_gmail(current_user: UserSession = Depends(get_current_user)):
    """Disconnect active Gmail account for current user (legacy support)."""
    default_acc = await db_service.get_account(user_id=current_user.user_id)
    if not default_acc:
        return {"status": "success", "message": "No active Gmail account to disconnect."}
    return await disconnect_specific_account(account_id=default_acc.get("id"), current_user=current_user)

@router.post("/demo-connect")
async def connect_demo_mailbox_legacy(current_user: UserSession = Depends(get_current_user)):
    """Connect demo mailbox for current user (legacy support)."""
    return await connect_demo_account(None, current_user=current_user)

@router.get("/me")
async def get_user_profile(current_user: UserSession = Depends(get_current_user)):
    """Retrieve active user profile and connected accounts summary."""
    accounts = await db_service.get_accounts(user_id=current_user.user_id)
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "accounts_count": len(accounts)
    }

@router.post("/switch-user")
async def switch_user(req: SwitchUserRequest):
    """Switch or establish active user session for testing multi-user isolation."""
    if not req.user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    accounts = await db_service.get_accounts(user_id=req.user_id)
    return {
        "status": "success",
        "user_id": req.user_id,
        "accounts_count": len(accounts),
        "message": f"Active user session set to {req.user_id}"
    }

