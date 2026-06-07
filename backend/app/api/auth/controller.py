"""Login controller - WorkOS authentication."""

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from app.api.deps import AuthServiceDep, CurrentUser
from app.core.auth.limiter import limiter
from app.core.auth.oauth_state import generate_oauth_state, validate_oauth_state
from app.database.schemas.User import UserPublic, UserRegister
from app.database.schemas.Utils import (
    AuthResponse,
    LoginRequest,
    Message,
    OAuthUrlResponse,
    SignupResponse,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse)
async def signup(
    auth_service: AuthServiceDep,
    signup_data: UserRegister,
) -> Any:
    """Create a new user with email and password.

    WorkOS will automatically send a verification email.
    User must verify email before they can login.
    """
    result = auth_service.signup(signup_request=signup_data)

    if result.error:
        raise result.error

    return SignupResponse(
        message="User has signed up succesfully",
        email=signup_data.email,
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Authenticate user with email and password via WorkOS.

    This endpoint authenticates against WorkOS and returns a session token
    that can be used for subsequent API requests.
    """
    result = auth_service.login(
        email=login_data.email,
        password=login_data.password,
        ip_address=request.client.host if request.client else None,
    )

    if result.is_err and result.error:
        raise result.error
    assert result.value is not None
    return AuthResponse(
        access_token=result.value["access_token"],
        user=UserPublic.model_validate(result.value["user"]),
    )


@router.get("/oauth/callback", response_model=AuthResponse)
@limiter.limit("10/minute")
def oauth_callback(
    request: Request,
    code: str,
    state: str,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Handle OAuth callback from provider.

    Exchanges the authorization code for user info and creates a session.

    Args:
        code: Authorization code from OAuth provider
        state: State token from OAuth callback (required)
    """
    ip = request.client.host if request.client else "unknown"

    try:
        state_payload = validate_oauth_state(state, ip)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    mode = state_payload.get("mode", "login")

    result = auth_service.oauth_callback(code=code, mode=mode)
    if result.is_err and result.error:
        raise result.error
    assert result.value is not None
    return AuthResponse(
        access_token=result.value["access_token"],
        user=UserPublic.model_validate(result.value["user"]),
    )


@router.get("/oauth/login/{provider}", response_model=OAuthUrlResponse)
def login_oauth(
    request: Request,
    provider: str,
    auth_service: AuthServiceDep,
) -> OAuthUrlResponse:
    """Get OAuth authorization URL for login flow.

    Args:
        provider: OAuth provider (google or github)

    Returns:
        JSON with authorization URL and state token
    """
    ip = request.client.host if request.client else "unknown"
    state = generate_oauth_state(mode="login", ip=ip)

    result = auth_service.get_oauth_url(provider=provider, state=state)

    if result.is_err and result.error:
        raise result.error

    auth_url = result.value
    if not auth_url:
        raise HTTPException(status_code=500, detail="No Auth URL")
    return OAuthUrlResponse(authorization_url=auth_url, state=state)


@router.get("/oauth/signup/{provider}", response_model=OAuthUrlResponse)
def signup_oauth(
    request: Request,
    provider: str,
    auth_service: AuthServiceDep,
) -> OAuthUrlResponse:
    """Get OAuth authorization URL for signup flow.

    Args:
        provider: OAuth provider (google or github)

    Returns:
        JSON with authorization URL and state token
    """
    ip = request.client.host if request.client else "unknown"
    state = generate_oauth_state(mode="signup", ip=ip)

    result = auth_service.get_oauth_url(provider=provider, state=state)

    if result.is_err and result.error:
        raise result.error

    auth_url = result.value
    if not auth_url:
        raise HTTPException(status_code=500, detail="No Auth URL")
    return OAuthUrlResponse(authorization_url=auth_url, state=state)


@router.post("/logout")
def logout(
    auth_service: AuthServiceDep,
    authorization: str | None = Header(None, alias="Authorization"),
) -> Message:
    """Logout current user."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

        # Get session_id from token and revoke it
        _ = auth_service.handle_logout(token)
        # Log error but don't fail - user is logging out anyway
    return Message(message="Successfully logged out")


@router.post("/verify-email")
@limiter.limit("5/minute")
def verify_email(
    request: Request, verify_request: VerifyEmailRequest, auth_service: AuthServiceDep
) -> Message:
    """Verify user's email with verification code.

    User must be authenticated to call this endpoint.

    Args:
        code: The verification code from the email
        email: User's email address
        pending_authentication_token: The token from the error response

    Returns:
        Success message
    """
    result = auth_service.verify_email(
        code=verify_request.code, email=verify_request.email
    )

    if result.is_err and result.error:
        raise result.error

    message = result.value
    if not message:
        return Message(message="Email verified!")

    return Message(message=message)


@router.post("/resend-verification")
@limiter.limit("3/minute")
def resend_verification_email(
    request: Request,
    email: str,
    auth_service: AuthServiceDep,
) -> Message:
    """Resend verification email to user.

    Args:
        email: User's email address

    Returns:
        Success message
    """
    result = auth_service.resend_verification_email(email=email)

    if result.is_err and result.error:
        raise result.error

    message = result.value
    if not message:
        return Message(message="Verification Sent!")

    return Message(message=message)


@router.get("/me", response_model=UserPublic)
def get_current_user_info(current_user: CurrentUser) -> UserPublic:
    """Get current authenticated user info."""
    return UserPublic.model_validate(current_user)


@router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> UserPublic:
    """Test if token is valid."""
    return UserPublic.model_validate(current_user)
