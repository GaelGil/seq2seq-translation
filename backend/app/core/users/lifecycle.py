from app.core.auth.workos import WorkOSAuthResult, WorkOSService
from app.database.models import User
from app.database.repositories.user import UserRepository
from app.database.schemas.Result import Result
from app.database.schemas.User import AuthProvider, UserCreate


class UserLifecycleError(Exception):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


class UserLifecycleService:
    def __init__(
        self,
        user_repo: UserRepository,
        workos_service: WorkOSService,
    ):
        self.user_repo = user_repo
        self.workos_service = workos_service

    def create_user(
        self,
        user_create: UserCreate,
    ) -> Result[User, UserLifecycleError]:
        user = User.model_validate(user_create)

        workos_result = self.workos_service.create_user(
            email=user.email,
            password=user_create.password,
            first_name=user.full_name,
        )
        if workos_result.is_err or not workos_result.value:
            return Result(
                value=None,
                error=UserLifecycleError(
                    workos_result.error.message
                    if workos_result.error
                    else "Failed to create WorkOS user",
                    code="WORKOS_CREATE_FAILED",
                ),
            )

        remote_ids = {"workos_user_id": workos_result.value.workos_user_id}
        user.workos_user_id = remote_ids["workos_user_id"]
        user.email_verified = False

        try:
            user = self.user_repo.create(user)
        except Exception as e:
            self._cleanup_remote_user(
                workos_user_id=remote_ids.get("workos_user_id"),
            )
            return Result(
                value=None,
                error=UserLifecycleError(
                    f"Failed to create local user: {e}",
                    code="LOCAL_CREATE_FAILED",
                ),
            )

        return Result(value=user, error=None)

    def create_user_from_sso(
        self,
        auth_result: WorkOSAuthResult,
        signup_code: str | None = None,
    ) -> Result[User, UserLifecycleError]:
        full_name = None
        if auth_result.first_name or auth_result.last_name:
            full_name = " ".join(
                filter(None, [auth_result.first_name, auth_result.last_name])
            )

        provider = (
            AuthProvider.google
            if auth_result.provider.lower() == "google"
            else AuthProvider.github
        )

        user = User(
            email=auth_result.email,
            full_name=full_name,
            hashed_password=None,
            workos_user_id=auth_result.workos_user_id,
            auth_provider=provider,
            email_verified=True,
            is_active=True,
            is_superuser=False,
        )

        remote_ids = {"workos_user_id": auth_result.workos_user_id}

        try:
            user = self.user_repo.create(user)
        except Exception as e:
            self._cleanup_remote_user(
                workos_user_id=remote_ids.get("workos_user_id"),
            )
            return Result(
                value=None,
                error=UserLifecycleError(
                    f"Failed to create local SSO user: {e}",
                    code="LOCAL_SSO_CREATE_FAILED",
                ),
            )

        return Result(value=user, error=None)

    def delete_user(self, user: User) -> Result[bool, UserLifecycleError]:
        if user.workos_user_id:
            workos_result = self.workos_service.delete_user(
                workos_id=user.workos_user_id
            )
            if workos_result.is_err:
                return Result(
                    value=False,
                    error=UserLifecycleError(
                        workos_result.error.message
                        if workos_result.error
                        else "Failed to delete WorkOS user",
                        code="WORKOS_DELETE_FAILED",
                    ),
                )

        self.user_repo.delete(user)
        return Result(value=True, error=None)

    def _cleanup_remote_user(
        self,
        workos_user_id: str | None,
    ) -> None:

        if workos_user_id:
            self.workos_service.delete_user(workos_id=workos_user_id)
