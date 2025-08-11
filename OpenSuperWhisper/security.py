"""
Security utilities for OpenSuperWhisper
Provides enhanced API key protection and secure storage
"""

import base64

from . import logger

# Conditional import of cryptography
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    logger.logger.warning("cryptography package not available - API key encryption disabled")
    CRYPTOGRAPHY_AVAILABLE = False


class APIKeyManager:
    """Secure API key storage with encryption"""

    def __init__(self) -> None:
        self.salt = b'opensuperwhisper_salt_v1'  # In production, use random salt per installation

    def _get_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_api_key(self, api_key: str, password: str) -> str:
        """Encrypt API key with password"""
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.logger.warning("Encryption not available - returning plain API key")
            return api_key
        try:
            key = self._get_key(password)
            f = Fernet(key)
            encrypted = f.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.logger.error(f"Failed to encrypt API key: {e}")
            raise

    def decrypt_api_key(self, encrypted_key: str, password: str) -> str | None:
        """Decrypt API key with password"""
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.logger.warning("Decryption not available - returning encrypted key as-is")
            return encrypted_key
        try:
            key = self._get_key(password)
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()  # type: ignore[no-any-return]
        except Exception as e:
            logger.logger.error(f"Failed to decrypt API key: {e}")
            return None

    def is_encrypted_key(self, key_value: str) -> bool:
        """Check if a key value appears to be encrypted"""
        # Encrypted keys will be base64 encoded and longer than normal API keys
        if not key_value:
            return False
        try:
            base64.urlsafe_b64decode(key_value.encode())
            return len(key_value) > 100 and not key_value.startswith('sk-')
        except Exception:
            return False


def secure_key_check(api_key: str) -> bool:
    """Validate API key format and security"""
    if not api_key:
        return False

    # Check for common API key patterns
    if api_key.startswith('sk-'):
        # OpenAI API key format
        if len(api_key) < 20:
            logger.logger.warning("API key appears too short")
            return False
        return True

    # Could be encrypted key
    manager = APIKeyManager()
    return manager.is_encrypted_key(api_key)


def sanitize_for_logs(text: str) -> str:
    """Sanitize sensitive information from log output"""
    if not text:
        return text

    # Replace API keys with masked version
    import re
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', 'sk-***MASKED***'),
        (r'Bearer [a-zA-Z0-9]{20,}', 'Bearer ***MASKED***'),
        (r'"api_key":\s*"[^"]{10,}"', '"api_key": "***MASKED***"'),
    ]

    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result
