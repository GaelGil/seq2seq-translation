"""WorkOS authentication service."""

import base64

import jwt
import workos
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import PyJWKClient

from app.core.config import settings
from app.database.schemas.Result import Result
from app.database.schemas.Utils import WorkOSAuthResult, WorkOSUserInfo


class WorkOSError(Exception):
    """Error from WorkOS service."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        pending_authentication_token: str | None = None,
    ):
        self.message = message
        self.code = code
        self.pending_authentication_token = pending_authentication_token
        super().__init__(message)


class WorkOSService:
    """Service for WorkOS User Management authentication."""

    def __init__(self) -> None:
        if not settings.WORKOS_API_KEY:
            raise WorkOSError("WORKOS_API_KEY not configured")
        if not settings.WORKOS_CLIENT_ID:
            raise WorkOSError("WORKOS_CLIENT_ID not configured")
        if not settings.WORKOS_REDIRECT_URI:
            raise WorkOSError("WORKOS_REDIRECT_URI not configured")

        self._client = workos.WorkOSClient(
            api_key=settings.WORKOS_API_KEY, client_id=settings.WORKOS_CLIENT_ID
        )
        self._redirect_uri = settings.WORKOS_REDIRECT_URI
        self._jwk_client: PyJWKClient | None = None

    def _resolve_signing_key(self, session_token: str) -> bytes | None:
        """Fetch JWKS from WorkOS and find the key matching the JWT's kid."""

        jwks = self._client.user_management.get_jwks(client_id=self._client.client_id)
        header = jwt.get_unverified_header(session_token)
        kid = header.get("kid")
        for key in jwks.keys:
            if key.kid == kid:
                n = int.from_bytes(base64.urlsafe_b64decode(key.n + "=="), "big")
                e = int.from_bytes(base64.urlsafe_b64decode(key.e + "=="), "big")
                pub_key = rsa.RSAPublicNumbers(e, n).public_key()
                pem = pub_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
                return pem
        return None

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Result[WorkOSUserInfo, WorkOSError]:
        """Create a new user with password in WorkOS.

        WorkOS will automatically send a verification email.

        Args:
            email: User's email address
            password: User's password
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            Tuple of (user_info, error)
        """
        try:
            user = self._client.user_management.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            return Result(
                value=WorkOSUserInfo(
                    workos_user_id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email_verified=user.email_verified,
                ),
                error=None,
            )

        except Exception as e:
            return Result(
                value=WorkOSUserInfo(
                    workos_user_id="",
                    email="",
                ),
                error=WorkOSError(f"Failed to create user: {str(e)}"),
            )

    def authenticate_with_password(
        self, email: str, password: str, ip_address: str | None = None
    ) -> Result[WorkOSAuthResult, WorkOSError]:
        """Authenticate user with email and password via WorkOS.

        Args:
            email: User's email address
            password: User's password
            ip_address: Optional IP address for security

        Returns:
            Result of (auth_result) or error
        """
        try:
            auth_response = self._client.user_management.authenticate_with_password(
                email=email,
                password=password,
                ip_address=ip_address,
            )

            user = auth_response.user
            access_token = auth_response.access_token

        except Exception as e:
            error_str = str(e)
            error_code = getattr(e, "code", None)

            # Try to extract pending_authentication_token from various locations
            pending_token = None

            if hasattr(e, "__dict__"):
                error_dict = e.__dict__

                # Check top level first
                pending_token = error_dict.get("pending_authentication_token")
                email_verification_id = error_dict.get("email_verification_id")

                # Check response_json
                if not pending_token or not email_verification_id:
                    response_json = error_dict.get("response_json", {})
                    pending_token = response_json.get("pending_authentication_token")

            # Check if email verification is required
            is_verification_required = (
                "email_verification_required" in error_str.lower()
                or error_code == "email_verification_required"
                or (error_code and "verification" in str(error_code).lower())
            )

            if is_verification_required:
                return Result(
                    value=WorkOSAuthResult(
                        workos_user_id="",
                        email=email,
                        provider="EmailPassword",
                    ),
                    error=WorkOSError(
                        message="Email verification required",
                        code="email_verification_required",
                        pending_authentication_token=pending_token,
                    ),
                )

            return Result(
                value=WorkOSAuthResult(
                    workos_user_id="",
                    email="",
                    provider="EmailPassword",
                ),
                error=WorkOSError(f"Authentication failed: {error_str}"),
            )

        return Result(
            value=WorkOSAuthResult(
                workos_user_id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                provider="EmailPassword",
                access_token=access_token,
            ),
            error=None,
        )

    def get_authorization_url(
        self,
        provider: str,
        state: str | None = None,
        login_hint: str | None = None,
    ) -> Result[str, WorkOSError]:
        """Generate WorkOS OAuth authorization URL for SSO.

        Args:
            provider: Auth provider (Google, GitHub)
            state: Optional state parameter for CSRF protection
            login_hint: Optional email to pre-fill

        Returns:
            Result of (authorization_url) or error
        """
        try:
            provider_map: dict[str, str] = {
                "google": "GoogleOAuth",
                "github": "GitHubOAuth",
            }
            provider_key = provider.lower()
            provider_literal = provider_map.get(provider_key)

            if not provider_literal:
                return Result(
                    value="",
                    error=WorkOSError(
                        f"Invalid provider: {provider}", code="INVALID_PROVIDER"
                    ),
                )

            url = self._client.user_management.get_authorization_url(
                redirect_uri=self._redirect_uri,
                provider=provider_literal,  # type: ignore[arg-type]
                state=state,
                login_hint=login_hint,
            )

            return Result(value=url, error=None)
        except Exception as e:
            return Result(
                value="", error=WorkOSError(f"Failed to create auth URL: {str(e)}")
            )

    def authenticate_with_code(
        self, code: str
    ) -> Result[WorkOSAuthResult, WorkOSError]:
        """Authenticate user with OAuth authorization code.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Result of (auth_result) or error
        """
        import time

        max_retries = 3
        retry_delay = 1  # second

        for attempt in range(max_retries):
            try:
                auth_response = self._client.user_management.authenticate_with_code(
                    code=code,
                )

                user = auth_response.user

                # Default provider - OAuth callbacks don't easily reveal the provider
                provider = "Google"

                return Result(
                    value=WorkOSAuthResult(
                        workos_user_id=user.id,
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        provider=provider,
                        access_token=auth_response.access_token,
                    ),
                    error=None,
                )
            except Exception as e:
                if attempt < max_retries - 1 and "500" in str(e):
                    time.sleep(retry_delay)
                    continue

                return Result(
                    value=None, error=WorkOSError(f"Authentication failed: {str(e)}")
                )

        return Result(
            value=None,
            error=WorkOSError("Authentication failed after multiple attempts"),
        )

    def validate_session(
        self, session_token: str
    ) -> Result[WorkOSUserInfo, WorkOSError]:
        """Validate a WorkOS session token and get user info.

        Args:
            session_token: The session token from WorkOS cookie

        Returns:
            Result of (user_info) or error
        """
        try:
            signing_key = self._resolve_signing_key(session_token)
            if signing_key is None:
                return Result(
                    value=None,
                    error=WorkOSError("No matching signing key found", code="INVALID"),
                )
            payload = jwt.decode(
                session_token,
                signing_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            return Result(
                value=WorkOSUserInfo(
                    workos_user_id=payload.get("sub", ""),
                    email=payload.get("email", ""),
                    first_name=payload.get("first_name"),
                    last_name=payload.get("last_name"),
                    email_verified=payload.get("email_verified", False),
                    session_id=payload.get("sid"),
                ),
                error=None,
            )
        except jwt.ExpiredSignatureError:
            return Result(
                value=None,
                error=WorkOSError("Session token has expired", code="EXPIRED"),
            )
        except jwt.InvalidTokenError as e:
            return Result(
                value=None,
                error=WorkOSError(f"Invalid session token: {str(e)}", code="INVALID"),
            )
        except Exception as e:
            return Result(
                value=None, error=WorkOSError(f"Session validation failed: {str(e)}")
            )

    def get_user(self, user_id: str) -> Result[WorkOSUserInfo, WorkOSError]:
        """Get user by ID from WorkOS.

        Args:
            user_id: WorkOS user ID

        Returns:
            Result of (user_info) or error
        """
        try:
            user = self._client.user_management.get_user(user_id=user_id)

            return Result(
                value=WorkOSUserInfo(
                    workos_user_id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email_verified=user.email_verified,
                ),
                error=None,
            )
        except Exception as e:
            return Result(
                value=None, error=WorkOSError(f"Failed to get user: {str(e)}")
            )

    def revoke_session(self, session_id: str) -> Result[bool, WorkOSError]:
        """Revoke a WorkOS session.

        Args:
            session_id: The session ID to revoke

        Returns:
            Result of (success) or error
        """
        try:
            self._client.user_management.revoke_session(session_id=session_id)
            return Result(value=True, error=None)
        except Exception as e:
            return Result(
                value=False, error=WorkOSError(f"Failed to revoke session: {str(e)}")
            )

    def send_verification_email(
        self, workos_user_id: str
    ) -> Result[WorkOSUserInfo, WorkOSError]:
        """Send email verification to a user.

        Args:
            workos_user_id: The WorkOS user ID

        Returns:
            Result of (user_info) or error
        """
        try:
            user = self._client.user_management.send_verification_email(
                user_id=workos_user_id
            )
            return Result(
                value=WorkOSUserInfo(
                    workos_user_id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email_verified=user.email_verified,
                ),
                error=None,
            )
        except Exception as e:
            return Result(
                value=None,
                error=WorkOSError(f"Failed to send verification email: {str(e)}"),
            )

    def verify_email(
        self, workos_user_id: str, code: str
    ) -> Result[WorkOSUserInfo, WorkOSError]:
        """Verify user's email with verification code.

        Args:
            workos_user_id: The WorkOS user ID
            code: The verification code from email

        Returns:
            Result of (user_info) or error
        """
        try:
            user = self._client.user_management.verify_email(
                user_id=workos_user_id,
                code=code,
            )
            return Result(
                value=WorkOSUserInfo(
                    workos_user_id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email_verified=user.email_verified,
                ),
                error=None,
            )
        except Exception as e:
            return Result(
                value=None, error=WorkOSError(f"Failed to verify email: {str(e)}")
            )

    def delete_user(self, workos_id: str) -> Result[bool, WorkOSError]:
        try:
            self._client.user_management.delete_user(id=workos_id)
            return Result(value=True, error=None)
        except Exception as e:
            return Result(
                value=False,
                error=WorkOSError(f"Failed to get verification status: {str(e)}"),
            )

    def update_password(
        self, workos_user_id: str, new_password: str
    ) -> Result[bool, WorkOSError]:
        """Update a user's password in WorkOS.

        Args:
            workos_user_id: The WorkOS user ID
            new_password: The new password to set

        Returns:
            Result of (success) or error
        """
        try:
            self._client.user_management.update_user(
                user_id=workos_user_id,
                password=new_password,
            )
            return Result(value=True, error=None)
        except Exception as e:
            return Result(
                value=False, error=WorkOSError(f"Failed to update password: {str(e)}")
            )


_workos_service: WorkOSService | None = None


def get_workos_service() -> WorkOSService:
    """Get WorkOS service singleton."""
    global _workos_service
    if _workos_service is None:
        _workos_service = WorkOSService()
    return _workos_service
