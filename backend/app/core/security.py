import base64
import hashlib
import logging
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
