from typing import Any

import jwt
from app.core.auth.workos import WorkOSAuthResult, WorkOSError, WorkOSService
from app.database.repositories.user import RepositoryError, UserRepository
from fastapi import HTTPException

from app.core.users import UserLifecycleError, UserLifecycleService
from app.database.models import User
from app.database.schemas.Result import Result
from app.database.schemas.User import UserCreate, UserRegister


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        workos_service: WorkOSService,
        user_lifecycle_service: UserLifecycleService,
    ):
        self.user_repo = user_repo
        self.workos_service = workos_service
        self.user_lifecycle_service = user_lifecycle_service

    def signup(
        self, signup_request: UserRegister, signup_code: str = ""
    ) -> Result[User, HTTPException]:
        """Create a new user with email and password.

        WorkOS will automatically send a verification email.
        User must verify email before they can login.

        Returns:
            Tuple of (success_message, None) or (None, HTTPException)
        """

        user_create = UserCreate.model_validate(signup_request)

        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            return Result(
                value=None,
                error=HTTPException(status_code=400, detail="Email already registered"),
            )

        try:
            lifecycle_result = self.user_lifecycle_service.create_user(
                user_create=user_create, signup_code=signup_code
            )
            if lifecycle_result.is_err:
                return Result(
                    value=None,
                    error=HTTPException(
                        status_code=400,
                        detail=lifecycle_result.error.message,
                    ),
                )
            return Result(value=lifecycle_result.value, error=None)
        except Exception as e:
            return Result(
                value=None, error=HTTPException(status_code=400, detail=str(e))
            )

    def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
    ) -> Result[dict, HTTPException]:
        """Authenticate user with email and password via WorkOS.

        Returns:
            Result of ({"access_token": ..., "user": ...}) or error
        """
        auth_result = self.workos_service.authenticate_with_password(
            email=email,
            password=password,
            ip_address=ip_address,
        )

        if (
            auth_result.is_err
            and auth_result.error.code == "email_verification_required"
        ):
            assert auth_result.error
            return Result(
                value=None,
                error=HTTPException(
                    status_code=403,
                    detail={
                        "code": "EMAIL_VERIFICATION_REQUIRED",
                        "pending_token": auth_result.error.pending_authentication_token
                        or "",
                        "message": "Email verification required. Please check your email for the verification code.",
                    },
                ),
            )

        if auth_result.is_err or not auth_result.value:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=401,
                    detail="Invalid email or password",
                ),
            )

        assert auth_result.value
        result = self._get_or_create_user(auth_result.value)

        if result.is_err:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=500,
                    detail=f"Authentication error: {result.error.message if result.error else 'Unknown error'}",
                ),
            )

        assert result.value
        if not result.value.is_active:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=403,
                    detail="User is inactive",
                ),
            )

        if not result.value.email_verified and result.value.workos_user_id:
            self.workos_service.send_verification_email(result.value.workos_user_id)
            return Result(
                value=None,
                error=HTTPException(
                    status_code=403,
                    detail="EMAIL_VERIFICATION_REQUIRED",
                ),
            )
        assert auth_result.value
        return Result(
            value={
                "access_token": auth_result.value.access_token,
                "user": result.value,
            },
            error=None,
        )

    def handle_logout(self, token: str) -> Result[bool, Any]:
        try:
            jwk_client = self.workos_service._get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            session_id = payload.get("sid")

            if not session_id:
                return Result(value=False, error=None)  # Can't revoke, but don't fail

            result = self.workos_service.revoke_session(session_id)
            if result.is_err:
                return Result(value=False, error=result.error)
            return Result(value=result.value, error=None)
        except Exception:
            return Result(value=False, error=None)

    def get_oauth_url(
        self,
        provider: str,
        state: str | None = None,
    ) -> Result[str, HTTPException]:
        """Get OAuth authorization URL for provider.

        Returns:
            Result of (authorization_url) or error
        """
        result = self.workos_service.get_authorization_url(
            provider=provider,
            state=state,
        )

        if result.is_err and result.error:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail=f"Failed to create authorization URL: {result.error.message}",
                ),
            )

        return Result(value=result.value, error=None)

    def oauth_callback(
        self, code: str, mode: str = "login"
    ) -> Result[dict, HTTPException]:
        """Handle OAuth callback from provider.

        Args:
            code: Authorization code from OAuth provider
            mode: "login" or "signup" - controls behavior for existing users

        Returns:
            Result of ({"access_token": ..., "user": ...}) or error
        """
        auth_result = self.workos_service.authenticate_with_code(code=code)
        if auth_result.is_err or not auth_result.value:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail=f"Authentication failed: {auth_result.error.message if auth_result.error else 'Invalid code'}",
                ),
            )
        if not auth_result.value:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail=f"Authentication failed: {auth_result.error.message if auth_result.error else 'Invalid code'}",
                ),
            )

        user_result = self._get_or_create_user(auth_result.value, mode=mode)
        if user_result.is_err or not user_result.value:
            return Result(value=None, error=user_result.error)

        user = user_result.value
        if not user.is_active:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=403,
                    detail="User is inactive",
                ),
            )

        if not user.email_verified:
            user.email_verified = True
            self.user_repo.update(user)

        return Result(
            value={
                "access_token": auth_result.value.access_token,
                "user": user,
            },
            error=None,
        )

    def verify_email(self, code: str, email: str) -> Result[str, HTTPException]:
        """Verify user's email with verification code.

        Returns:
            Result of (success_message) or error
        """
        user = self.user_repo.get_by_email(email)

        if not user:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail="User not linked to WorkOS",
                ),
            )

        if not user.workos_user_id:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail="User not linked to WorkOS",
                ),
            )

        result = self.workos_service.verify_email(
            user.workos_user_id,
            code,
        )

        if result.is_err or not result.value:
            return Result(
                value=None,
                error=HTTPException(
                    status_code=400,
                    detail=result.error.message
                    if result.error
                    else "Invalid verification code",
                ),
            )

        user.email_verified = True
        self.user_repo.update(user)

        return Result(value="Email verified successfully", error=None)

    def resend_verification_email(self, email: str) -> Result[str, WorkOSError]:
        """Resend verification email to user.

        Returns:
            Result of (success_message) or error
        """
        user = self.user_repo.get_by_email(email)

        if not user:
            return Result(
                value="If the email exists, a verification email has been sent",
                error=None,
            )

        if not user.workos_user_id:
            return Result(value="User not linked to WorkOS", error=None)

        if user.email_verified:
            return Result(value="Email is already verified", error=None)

        result = self.workos_service.send_verification_email(user.workos_user_id)

        if result.is_err and result.error:
            return Result(value="Failed to send verification email", error=result.error)

        return Result(value="Verification email sent", error=None)

    def _get_or_create_user(
        self, auth_result: WorkOSAuthResult, mode: str = "login"
    ) -> Result[User | None, RepositoryError | UserLifecycleError | HTTPException]:
        """Find or create user from WorkOS authentication result.

        Args:
            auth_result: WorkOS authentication result
            mode: "login" or "signup" - controls behavior for existing users

        Returns:
            Result of (user) or error
        """
        user = self.user_repo.get_by_workos_user_id(auth_result.workos_user_id)

        if user:
            result = self.user_repo.update_user_from_sso(user, auth_result)
            if result.is_err:
                return Result(value=None, error=result.error)
            return Result(value=result.value, error=None)

        existing_user = self.user_repo.get_by_email(auth_result.email)

        if existing_user:
            if mode == "signup":
                return Result(
                    value=None,
                    error=HTTPException(
                        status_code=400,
                        detail="Email already registered. Please login instead.",
                    ),
                )
            result = self.user_repo.link_workos_user(
                existing_user,
                auth_result.workos_user_id,
                auth_result.provider,
            )
            if result.is_err:
                return Result(value=None, error=result.error)
            return Result(value=result.value, error=None)

        if mode == "login":
            return Result(
                value=None,
                error=HTTPException(
                    status_code=404,
                    detail="No account found with this provider. Please sign up first.",
                ),
            )

        result = self.user_lifecycle_service.create_user_from_sso(auth_result)
        if result.is_err:
            return Result(value=None, error=result.error)
        return Result(value=result.value, error=None)
