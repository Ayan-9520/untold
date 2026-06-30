"""Field-level encryption for secrets at rest."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


def _encryption_material(settings=None) -> str:
    """Key material for Fernet — prefers ENCRYPTION_KEY, falls back to SECRET_KEY."""
    settings = settings or get_settings()
    return settings.encryption_key or settings.secret_key


def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(_encryption_material().encode()).digest())
    return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt secret") from exc
