"""
Security utilities using pure Python (no cryptography dependency).
Uses HMAC-SHA256 for JWT signing and hashlib + secrets for password hashing.
"""
import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings

# bcrypt-like password hashing using PBKDF2 (built-in)
_ITERATIONS = 260000
_HASH_NAME = "sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(_HASH_NAME, password.encode(), salt.encode(), _ITERATIONS)
    return f"pbkdf2:{salt}:{dk.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        _, salt, stored_hex = hashed.split(":", 2)
        dk = hashlib.pbkdf2_hmac(_HASH_NAME, plain.encode(), salt.encode(), _ITERATIONS)
        return hmac.compare_digest(dk.hex(), stored_hex)
    except Exception:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    if pad != 4:
        s += "=" * pad
    return base64.urlsafe_b64decode(s)


def _sign(header_b64: str, payload_b64: str, secret: str) -> str:
    msg = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    return _b64url_encode(sig)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "type": "access",
        "jti": secrets.token_hex(16),
    }
    if extra:
        payload.update(extra)
    return _encode_token(payload)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "type": "refresh",
        "jti": secrets.token_hex(16),
    }
    return _encode_token(payload)


def _encode_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = _sign(header_b64, payload_b64, settings.SECRET_KEY)
    return f"{header_b64}.{payload_b64}.{sig}"


def decode_token(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    header_b64, payload_b64, provided_sig = parts
    expected_sig = _sign(header_b64, payload_b64, settings.SECRET_KEY)

    if not hmac.compare_digest(provided_sig, expected_sig):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_b64))

    exp = payload.get("exp")
    if exp and datetime.now(timezone.utc).timestamp() > exp:
        raise ValueError("Token expired")

    return payload


def generate_api_key() -> str:
    return f"gak_{secrets.token_urlsafe(32)}"
