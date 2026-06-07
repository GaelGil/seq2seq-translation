"""Login controller - WorkOS authentication."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import AuthServiceDep, EventBusDep
from app.database.schemas.User import UserRegister
from app.database.schemas.Utils import (
    SignupResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse)
async def signup(
    auth_service: AuthServiceDep,
    events: EventBusDep,
    signup_data: UserRegister,
) -> Any:
    pass
