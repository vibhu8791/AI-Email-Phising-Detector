import base64
import hashlib
import json
import logging
import time
import uuid
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from app.core.config import settings

logger = logging.getLogger("app.security")

def _get_fernet_key(raw_key: str) -> bytes:
    """Derive a consistent 32-byte urlsafe base64 Fernet key from raw string."""
    digest = hashlib.sha256(raw_key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)

_cipher = Fernet(_get_fernet_key(settings.SECRET_KEY))

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

def generate_oauth_state(user_id: str = "default_user") -> str:
    """
    Generate a tamper-proof, time-bound OAuth state token bound to the requesting user_id.
    Prevents CSRF and links callback securely to the initiating user.
    """
    payload = {
        "user_id": user_id,
        "nonce": uuid.uuid4().hex,
        "created_at": time.time()
    }
    encoded_json = json.dumps(payload).encode('utf-8')
    return _cipher.encrypt(encoded_json).decode('utf-8')

def verify_oauth_state(state: str, max_age_seconds: int = 600) -> Optional[Dict[str, Any]]:
    """
    Verify and decode the OAuth state token.
    Enforces maximum age (default 10 minutes) and integrity.
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

