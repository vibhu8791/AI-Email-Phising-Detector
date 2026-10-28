import base64
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import jwt
from app.core.config import settings

logger = logging.getLogger("app.security")

def _get_fernet_key(raw_key: str) -> bytes:
    """Derive a consistent 32-byte urlsafe base64 Fernet key from raw string."""
    digest = hashlib.sha256(raw_key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)

_cipher = Fernet(_get_fernet_key(settings.SECRET_KEY))

# =========================================================================
# TOKEN ENCRYPTION AT REST (FERNET / AES)
# =========================================================================

def encrypt_token(plain_token: str) -> str:
    """Encrypt OAuth token before persisting in database."""
    if not plain_token:
        return ""
    try:
        encrypted_bytes = _cipher.encrypt(plain_token.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Error encrypting token: {e}")
        return plain_token

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt stored OAuth token for API consumption."""
    if not encrypted_token:
        return ""
    try:
        decrypted_bytes = _cipher.decrypt(encrypted_token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Error decrypting token: {e}")
        return encrypted_token

# =========================================================================
# SERVER-SIDE JWT AUTHENTICATION
# =========================================================================

def create_access_token(
    user_id: str, 
    email: Optional[str] = None, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a cryptographically signed JWT access token for an authenticated user.
    Uses HS256 and settings.effective_jwt_secret.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    payload = {
        "sub": str(user_id),
        "email": email or f"{user_id}@workspace.local",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "ai-phishing-shield",
        "type": "access"
    }

    token = jwt.encode(payload, settings.effective_jwt_secret, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token server-side.
    Enforces signature validity, expiration, and issuer.
    Returns decoded payload if valid, None if invalid or expired.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="ai-phishing-shield"
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Access token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid access token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating access token: {e}")
        return None

# =========================================================================
# TAMPER-PROOF OAUTH STATE (CSRF & USER BINDING)
# =========================================================================

def generate_oauth_state(user_id: str, action: str = "connect_gmail") -> str:
    """
    Generate a tamper-proof, time-bound OAuth state token bound to the requesting user_id.
    Prevents CSRF and links callback securely to the initiating application user.
    """
    payload = {
        "user_id": user_id,
        "action": action,
        "nonce": uuid.uuid4().hex,
        "created_at": time.time()
    }
    encoded_json = json.dumps(payload).encode('utf-8')
    return _cipher.encrypt(encoded_json).decode('utf-8')

def verify_oauth_state(state: str, max_age_seconds: int = 600) -> Optional[Dict[str, Any]]:
    """
    Verify and decode the OAuth state token.
    Enforces maximum age (default 10 minutes) and cryptographic integrity.
    """
    if not state:
        return None
    try:
        decrypted_bytes = _cipher.decrypt(state.encode('utf-8'), ttl=max_age_seconds)
        data = json.loads(decrypted_bytes.decode('utf-8'))
        return data
    except Exception as e:
        logger.warning(f"Invalid or expired OAuth state parameter: {e}")
        return None
