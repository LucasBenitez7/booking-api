"""
Development-only router — only registered when APP_ENV=development.
Provides seed and reset endpoints for local testing and Postman automation.
Never available in production.
"""

from datetime import UTC, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.deps import get_db_session, get_jwt_service, get_password_hasher
from booking.domain.ports.password_hasher import PasswordHasher
from booking.infrastructure.persistence.models.space_model import SpaceModel
from booking.infrastructure.persistence.models.user_model import UserModel
from booking.infrastructure.security.jwt_service import JwtService

router = APIRouter(prefix="/dev", tags=["dev"])

_ADMIN_EMAIL = "admin@booking-api.com"
_ADMIN_PASSWORD = "Admin1234!"  # nosec B105 — fixed demo credential, not a real secret
_USER_EMAIL = "user@booking-api.com"
_USER_PASSWORD = "User1234!"  # nosec B105 — fixed demo credential, not a real secret


@router.post("/seed", summary="Create demo admin + regular user + 3 spaces")
async def seed(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> dict[str, object]:
    """
    Idempotent: if admin already exists, skips creation and returns a fresh token.
    Safe to call multiple times.
    """
    from sqlalchemy import select

    now = datetime.now(tz=UTC)

    # --- Admin user ---
    existing = await session.execute(
        select(UserModel).where(UserModel.email == _ADMIN_EMAIL)
    )
    admin_model = existing.scalar_one_or_none()

    if admin_model is None:
        admin_hashed = await hasher.hash_password(_ADMIN_PASSWORD)
        admin_model = UserModel(
            id=_new_id(),
            email=_ADMIN_EMAIL,
            full_name="Demo Admin",
            hashed_password=admin_hashed,
            is_active=True,
            is_admin=True,
            max_active_bookings=100,
            created_at=now,
        )
        session.add(admin_model)

    # --- Regular user ---
    existing_user = await session.execute(
        select(UserModel).where(UserModel.email == _USER_EMAIL)
    )
    if existing_user.scalar_one_or_none() is None:
        user_hashed = await hasher.hash_password(_USER_PASSWORD)
        session.add(
            UserModel(
                id=_new_id(),
                email=_USER_EMAIL,
                full_name="Demo User",
                hashed_password=user_hashed,
                is_active=True,
                is_admin=False,
                max_active_bookings=5,
                created_at=now,
            )
        )

    # --- Spaces (only if none exist) ---
    spaces_result = await session.execute(select(SpaceModel))
    if not spaces_result.scalars().all():
        spaces = [
            SpaceModel(
                id=_new_id(),
                name="Meeting Room A",
                description="Main meeting room with projector, capacity for 10.",
                capacity=10,
                price_per_hour=25.0,
                is_active=True,
                min_duration_minutes=30,
                max_duration_minutes=480,
                min_advance_minutes=60,
                cancellation_deadline_hours=24,
                opening_time=time(8, 0),
                closing_time=time(22, 0),
                created_at=now,
            ),
            SpaceModel(
                id=_new_id(),
                name="Private Office B",
                description="Private office with desk and ergonomic chair, capacity for 2.",
                capacity=2,
                price_per_hour=15.0,
                is_active=True,
                min_duration_minutes=30,
                max_duration_minutes=480,
                min_advance_minutes=60,
                cancellation_deadline_hours=24,
                opening_time=time(8, 0),
                closing_time=time(22, 0),
                created_at=now,
            ),
            SpaceModel(
                id=_new_id(),
                name="Open Coworking",
                description="Open space with 20 workstations.",
                capacity=20,
                price_per_hour=10.0,
                is_active=True,
                min_duration_minutes=30,
                max_duration_minutes=480,
                min_advance_minutes=60,
                cancellation_deadline_hours=24,
                opening_time=time(8, 0),
                closing_time=time(22, 0),
                created_at=now,
            ),
        ]
        for s in spaces:
            session.add(s)

    await session.commit()
    await session.refresh(admin_model)

    access_token = jwt_service.create_access_token(admin_model.id)

    return {
        "message": "Seed completed",
        "admin_email": _ADMIN_EMAIL,
        "admin_password": _ADMIN_PASSWORD,
        "user_email": _USER_EMAIL,
        "user_password": _USER_PASSWORD,
        "access_token": access_token,
        "token_type": "bearer",  # nosec B105 — OAuth2 token type string, not a password
    }


@router.delete("/reset", summary="Wipe all bookings, spaces and users")
async def reset(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    """
    Deletes all rows from bookings, spaces and users tables.
    Useful to start the Postman collection from a clean state.
    """
    from booking.infrastructure.persistence.models.booking_model import BookingModel

    await session.execute(delete(BookingModel))
    await session.execute(delete(SpaceModel))
    await session.execute(delete(UserModel))
    await session.commit()
    return {"message": "All data wiped — database is clean"}


def _new_id() -> str:
    import uuid

    return str(uuid.uuid4())
