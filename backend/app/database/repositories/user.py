"""User repository for data access operations."""

from typing import Any

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.auth.workos import WorkOSAuthResult
from app.core.security import get_password_hash
from app.database.models import User
from app.database.repositories.base import BaseRepository
from app.database.schemas.Result import Result
from app.database.schemas.User import AuthProvider, UserCreate, UserUpdate, UserUpdateMe


class RepositoryError:
    """Error class for repository operations."""

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code


class UserRepository(BaseRepository[User]):
    """Repository for User-related database operations."""

    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_workos_user_id(self, workos_user_id: str) -> User | None:
        """Get a user by WorkOS user ID."""
        statement = select(User).where(User.workos_user_id == workos_user_id)
        return self.session.exec(statement).first()

    def create_user(self, user_create: UserCreate, signup_code: str = "") -> User:
        """Create a local DB user with wallet only."""
        user = User.model_validate(user_create)
        user.hashed_password = get_password_hash(user_create.password)
        return self.create(user)

    def create_user_from_sso(
        self,
        auth_result: WorkOSAuthResult,
        signup_code: str | None = None,
    ) -> Result[User, RepositoryError]:
        """Create a local DB SSO user with wallet only."""
        try:
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
                hashed_password=None,  # No password for SSO users
                workos_user_id=auth_result.workos_user_id,
                auth_provider=provider,
                email_verified=True,
                is_active=True,
                is_superuser=False,
            )

            user = self.create(user)

            return Result(value=user, error=None)
        except Exception as e:
            return Result(
                value=None,
                error=RepositoryError(message=str(e), code="CREATE_USER_FAILED"),
            )

    def link_workos_user(
        self, db_user: User, workos_user_id: str, provider: str
    ) -> Result[User, RepositoryError]:
        """Link an existing user to a WorkOS identity.

        Args:
            db_user: The existing user to link
            workos_user_id: The WorkOS user ID
            provider: The SSO provider (google, github)

        Returns:
            Result of (updated_user) or error
        """
        try:
            # Determine provider value
            provider_value: str = "google" if provider.lower() == "google" else "github"

            db_user.workos_user_id = workos_user_id
            db_user.auth_provider = provider_value  # type: ignore[assignment]
            db_user.email_verified = True

            db_user = self.update(obj=db_user)

            return Result(value=db_user, error=None)
        except Exception as e:
            return Result(
                value=None,
                error=RepositoryError(message=str(e), code="LINK_USER_FAILED"),
            )

    def authenticate_workos(self, workos_user_id: str) -> Result[User, RepositoryError]:
        """Authenticate a user by WorkOS user ID.

        Args:
            workos_user_id: The WorkOS user ID

        Returns:
            Result of (user) or error
        """
        user = self.get_by_workos_user_id(workos_user_id)
        if not user:
            return Result(
                value=None,
                error=RepositoryError(
                    message="User not found with this WorkOS ID",
                    code="USER_NOT_FOUND",
                ),
            )
        if not user.is_active:
            return Result(
                value=None,
                error=RepositoryError(message="User is inactive", code="INACTIVE_USER"),
            )
        return Result(value=user, error=None)

    def update_user_from_sso(
        self, db_user: User, auth_result: WorkOSAuthResult
    ) -> Result[User, RepositoryError]:
        """Update user profile from SSO authentication result.

        Args:
            db_user: The user to update
            auth_result: WorkOS authentication result

        Returns:
            Result of (updated_user) or error
        """
        try:
            if auth_result.first_name or auth_result.last_name:
                db_user.full_name = " ".join(
                    filter(None, [auth_result.first_name, auth_result.last_name])
                )

            db_user.email_verified = True

            db_user = self.update(obj=db_user)

            return Result(value=db_user, error=None)
        except Exception as e:
            return Result(
                value=None,
                error=RepositoryError(message=str(e), code="UPDATE_USER_FAILED"),
            )

    def update_user(self, user: User, user_in: UserUpdate | UserUpdateMe) -> User:
        """Update an existing user.

        Args:
            db_user: The existing user to update
            user_in: Update schema with fields to change

        Returns:
            The updated user
        """

        if user_in.email:
            existing_user = self.get_by_email(email=user_in.email)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=409, detail="User with this email already exists"
                )
        user_data = user_in.model_dump(exclude_unset=True)
        user.sqlmodel_update(user_data)

        user_data = user_in.model_dump(exclude_unset=True)
        extra_data: dict[str, Any] = {}

        # Password updates are handled by WorkOS, not here
        user_data.pop("password", None)

        user.sqlmodel_update(user_data, update=extra_data)
        db_user = self.update(obj=user)

        return db_user

    def delete_user(self, user: User) -> Result[bool, None]:
        self.delete(obj=user)
        return Result(value=True, error=None)
