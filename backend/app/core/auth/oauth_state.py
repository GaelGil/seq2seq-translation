"""OAuth state generation and validation utilities."""

import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from app.core.config import settings

STATE_EXPIRE_MINUTES = 5


def generate_oauth_state(mode: str, ip: str) -> str:
    """Generate signed OAuth state JWT.

    Args:
        mode: "login" or "signup"
        ip: Client IP address

    Returns:
        Signed JWT string containing state metadata
    """
    payload = {
        "sub": secrets.token_urlsafe(16),
        "ip": ip,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=STATE_EXPIRE_MINUTES),
        "mode": mode,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def validate_oauth_state(state: str, ip: str) -> dict:
    """Validate OAuth state JWT.

    Args:
        state: JWT string from OAuth callback
        ip: Client IP address

    Returns:
        Decoded payload if valid

    Raises:
        HTTPException: If state is invalid, expired, or IP mismatch
    """
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid state token")

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        raise HTTPException(status_code=400, detail="State token expired")

    if payload["ip"] != ip:
        raise HTTPException(status_code=400, detail="IP address mismatch")

    return payload
