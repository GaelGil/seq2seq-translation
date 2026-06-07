from typing import Literal

from sqlmodel import Field, SQLModel

from app.database.schemas.User import UserPublic


class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class LoginRequest(SQLModel):
    """Request body for email/password login."""

    email: str
    password: str


class AuthResponse(SQLModel):
    """Response containing session token."""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class SignupRequest(SQLModel):
    """Request body for email/password signup."""

    email: str
    password: str
    full_name: str | None = None


class SignupResponse(SQLModel):
    """Response after successful signup."""

    message: str
    email: str


class OAuthUrlResponse(SQLModel):
    """Response containing OAuth authorization URL."""

    authorization_url: str
    state: str


class WorkOSAuthResult(SQLModel):
    """Result from WorkOS authentication."""

    workos_user_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    provider: Literal["Google", "GitHub", "SAML", "EmailPassword"] = "EmailPassword"
    access_token: str | None = None


class WorkOSUserInfo(SQLModel):
    """User info from WorkOS session."""

    workos_user_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    email_verified: bool = False
    session_id: str | None = None


class VerifyEmailRequest(SQLModel):
    """Request body for verifying email during login."""

    code: str
    pending_authentication_token: str
    email: str
