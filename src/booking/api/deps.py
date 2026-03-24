from collections.abc import AsyncGenerator
from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from booking.application.use_cases.admin_spaces import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    UpdateSpaceUseCase,
)
from booking.application.use_cases.cancel_booking import CancelBookingUseCase
from booking.application.use_cases.confirm_password_reset import (
    ConfirmPasswordResetUseCase,
)
from booking.application.use_cases.create_booking import CreateBookingUseCase
from booking.application.use_cases.get_availability import GetAvailabilityUseCase
from booking.application.use_cases.get_booking import GetBookingUseCase
from booking.application.use_cases.list_admin_bookings import ListAdminBookingsUseCase
from booking.application.use_cases.list_spaces import GetSpaceUseCase, ListSpacesUseCase
from booking.application.use_cases.list_user_bookings import ListUserBookingsUseCase
from booking.application.use_cases.login_user import LoginUserUseCase
from booking.application.use_cases.refresh_access_token import RefreshAccessTokenUseCase
from booking.application.use_cases.register_user import RegisterUserUseCase
from booking.application.use_cases.request_password_reset import (
    RequestPasswordResetUseCase,
)
from booking.application.use_cases.update_booking import UpdateBookingUseCase
from booking.application.use_cases.update_user_admin import UpdateUserAdminUseCase
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import (
    AdminRequiredError,
    AuthenticationError,
)
from booking.domain.ports.auth_token_issuer import AuthTokenIssuer
from booking.domain.ports.notification_service import NotificationService
from booking.domain.ports.password_hasher import PasswordHasher
from booking.domain.ports.password_reset_token_store import PasswordResetTokenStore
from booking.domain.value_objects.booking_id import BookingId
from booking.infrastructure.config.settings import Settings
from booking.infrastructure.persistence.database import get_session
from booking.infrastructure.persistence.repositories.sqlalchemy_booking_repo import (
    SQLAlchemyBookingRepository,
)
from booking.infrastructure.persistence.repositories.sqlalchemy_space_repo import (
    SQLAlchemySpaceRepository,
)
from booking.infrastructure.persistence.repositories.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)
from booking.infrastructure.security.jwt_service import JwtService


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_jwt_service(request: Request) -> JwtService:
    return cast(JwtService, request.app.state.jwt_service)


def get_auth_token_issuer(request: Request) -> AuthTokenIssuer:
    return cast(AuthTokenIssuer, request.app.state.jwt_service)


def get_password_hasher(request: Request) -> PasswordHasher:
    return cast(PasswordHasher, request.app.state.password_hasher)


def get_password_reset_store(request: Request) -> PasswordResetTokenStore:
    return cast(PasswordResetTokenStore, request.app.state.password_reset_store)


def get_notification_service(request: Request) -> NotificationService:
    return cast(NotificationService, request.app.state.notification_service)


def get_register_user_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        SQLAlchemyUserRepository(session),
        password_hasher,
    )


def get_login_user_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> LoginUserUseCase:
    return LoginUserUseCase(SQLAlchemyUserRepository(session), password_hasher)


def get_refresh_access_token_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    tokens: Annotated[AuthTokenIssuer, Depends(get_auth_token_issuer)],
) -> RefreshAccessTokenUseCase:
    return RefreshAccessTokenUseCase(SQLAlchemyUserRepository(session), tokens)


def get_request_password_reset_use_case(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    store: Annotated[PasswordResetTokenStore, Depends(get_password_reset_store)],
    notification: Annotated[NotificationService, Depends(get_notification_service)],
) -> RequestPasswordResetUseCase:
    settings = request.app.state.settings
    return RequestPasswordResetUseCase(
        SQLAlchemyUserRepository(session),
        store,
        notification,
        settings.password_reset_token_ttl_seconds,
    )


def get_confirm_password_reset_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    store: Annotated[PasswordResetTokenStore, Depends(get_password_reset_store)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> ConfirmPasswordResetUseCase:
    return ConfirmPasswordResetUseCase(
        SQLAlchemyUserRepository(session),
        store,
        password_hasher,
    )


def get_create_booking_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    notification: Annotated[NotificationService, Depends(get_notification_service)],
) -> CreateBookingUseCase:
    return CreateBookingUseCase(
        SQLAlchemyBookingRepository(session),
        SQLAlchemySpaceRepository(session),
        SQLAlchemyUserRepository(session),
        notification,
    )


def get_cancel_booking_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    notification: Annotated[NotificationService, Depends(get_notification_service)],
) -> CancelBookingUseCase:
    return CancelBookingUseCase(
        SQLAlchemyBookingRepository(session),
        SQLAlchemySpaceRepository(session),
        SQLAlchemyUserRepository(session),
        notification,
    )


def get_update_booking_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateBookingUseCase:
    return UpdateBookingUseCase(
        SQLAlchemyBookingRepository(session),
        SQLAlchemySpaceRepository(session),
        SQLAlchemyUserRepository(session),
    )


def get_list_user_bookings_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ListUserBookingsUseCase:
    return ListUserBookingsUseCase(SQLAlchemyBookingRepository(session))


def get_get_booking_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetBookingUseCase:
    return GetBookingUseCase(
        SQLAlchemyBookingRepository(session),
        SQLAlchemyUserRepository(session),
    )


def get_get_availability_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetAvailabilityUseCase:
    return GetAvailabilityUseCase(
        SQLAlchemyBookingRepository(session),
        SQLAlchemySpaceRepository(session),
    )


def get_list_admin_bookings_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ListAdminBookingsUseCase:
    return ListAdminBookingsUseCase(SQLAlchemyBookingRepository(session))


def get_create_space_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateSpaceUseCase:
    return CreateSpaceUseCase(SQLAlchemySpaceRepository(session))


def get_update_space_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateSpaceUseCase:
    return UpdateSpaceUseCase(SQLAlchemySpaceRepository(session))


def get_delete_space_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeleteSpaceUseCase:
    return DeleteSpaceUseCase(SQLAlchemySpaceRepository(session))


def get_list_spaces_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ListSpacesUseCase:
    return ListSpacesUseCase(SQLAlchemySpaceRepository(session))


def get_get_space_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetSpaceUseCase:
    return GetSpaceUseCase(SQLAlchemySpaceRepository(session))


def get_update_user_admin_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateUserAdminUseCase:
    return UpdateUserAdminUseCase(SQLAlchemyUserRepository(session))


async def get_current_user_id(
    request: Request,
    tokens: Annotated[AuthTokenIssuer, Depends(get_auth_token_issuer)],
) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid Authorization header")
    token = auth.removeprefix("Bearer ").strip()
    return tokens.decode_access_token(token)


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    uid = BookingId.from_string(user_id)
    user = await SQLAlchemyUserRepository(session).find_by_id(uid)
    if user is None:
        raise AuthenticationError("User not found")
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise AdminRequiredError()
    return user
