"""TOTP-based two-factor authentication."""

from __future__ import annotations

import hashlib
import secrets

import pyotp

from app.domain.security.encryption import decrypt_value, encrypt_value


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_provisioning_uri(secret: str, email: str, issuer: str = "UNTOLD Studio") -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, code: str, *, encrypted: bool = False) -> bool:
    raw = decrypt_value(secret) if encrypted else secret
    totp = pyotp.TOTP(raw)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 8) -> list[str]:
    return [secrets.token_hex(4).upper() for _ in range(count)]


def hash_backup_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def verify_backup_code(code: str, hashes: list[str]) -> bool:
    h = hash_backup_code(code)
    return h in hashes


def encrypt_totp_secret(secret: str) -> str:
    return encrypt_value(secret)
