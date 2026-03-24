from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.deps import (
    get_create_space_use_case,
    get_current_admin,
    get_db_session,
    get_delete_space_use_case,
    get_list_admin_bookings_use_case,
    get_update_space_use_case,
    get_update_user_admin_use_case,
)
from booking.api.routers.spaces import _space_to_public
from booking.api.schemas.admin_schemas import AdminUserUpdateBody
from booking.api.schemas.booking_schemas import BookingPublic
from booking.api.schemas.space_schemas import (
    SpaceCreateBody,
    SpacePublic,
    SpaceUpdateBody,
)
from booking.application.dtos.admin_dtos import (
    CreateSpaceAdminDTO,
    ListAdminBookingsDTO,
    UpdateSpaceAdminDTO,
    UpdateUserAdminDTO,
)
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.application.use_cases.admin_spaces import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    UpdateSpaceUseCase,
)
from booking.application.use_cases.list_admin_bookings import ListAdminBookingsUseCase
from booking.application.use_cases.update_user_admin import UpdateUserAdminUseCase
from booking.infrastructure.persistence.repositories.sqlalchemy_space_repo import (
    SQLAlchemySpaceRepository,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


def _booking_to_public(dto: BookingResponseDTO) -> BookingPublic:
    return BookingPublic(
        id=dto.id,
        space_id=dto.space_id,
        user_id=dto.user_id,
        start=dto.start,
        end=dto.end,
        status=dto.status,
        notes=dto.notes,
        created_at=dto.created_at,
    )


@router.get("/bookings", response_model=list[BookingPublic])
async def admin_list_bookings(
    use_case: Annotated[
        ListAdminBookingsUseCase, Depends(get_list_admin_bookings_use_case)
    ],
    status: str | None = None,
) -> list[BookingPublic]:
    results = await use_case.execute(ListAdminBookingsDTO(status=status))
    return [_booking_to_public(r) for r in results]


@router.get("/spaces", response_model=list[SpacePublic])
async def admin_list_spaces(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[SpacePublic]:
    repo = SQLAlchemySpaceRepository(session)
    spaces = await repo.find_all(active_only=False)
    return [_space_to_public(s) for s in spaces]


@router.post("/spaces", response_model=SpacePublic)
async def admin_create_space(
    body: SpaceCreateBody,
    use_case: Annotated[CreateSpaceUseCase, Depends(get_create_space_use_case)],
) -> SpacePublic:
    space = await use_case.execute(
        CreateSpaceAdminDTO(
            name=body.name,
            description=body.description,
            capacity=body.capacity,
            price_per_hour=body.price_per_hour,
        )
    )
    return _space_to_public(space)


@router.patch("/spaces/{space_id}", response_model=SpacePublic)
async def admin_update_space(
    space_id: str,
    body: SpaceUpdateBody,
    use_case: Annotated[UpdateSpaceUseCase, Depends(get_update_space_use_case)],
) -> SpacePublic:
    space = await use_case.execute(
        UpdateSpaceAdminDTO(
            space_id=space_id,
            name=body.name,
            description=body.description,
            capacity=body.capacity,
            price_per_hour=body.price_per_hour,
            min_duration_minutes=body.min_duration_minutes,
            max_duration_minutes=body.max_duration_minutes,
            min_advance_minutes=body.min_advance_minutes,
            cancellation_deadline_hours=body.cancellation_deadline_hours,
            opening_time=body.opening_time,
            closing_time=body.closing_time,
            is_active=body.is_active,
        )
    )
    return _space_to_public(space)


@router.delete("/spaces/{space_id}")
async def admin_delete_space(
    space_id: str,
    use_case: Annotated[DeleteSpaceUseCase, Depends(get_delete_space_use_case)],
) -> dict[str, str]:
    await use_case.execute(space_id)
    return {"detail": "Space deactivated"}


@router.patch("/users/{user_id}", response_model=dict[str, object])
async def admin_update_user(
    user_id: str,
    body: AdminUserUpdateBody,
    use_case: Annotated[
        UpdateUserAdminUseCase, Depends(get_update_user_admin_use_case)
    ],
) -> dict[str, object]:
    user = await use_case.execute(
        UpdateUserAdminDTO(
            user_id=user_id,
            max_active_bookings=body.max_active_bookings,
            is_admin=body.is_admin,
        )
    )
    return {
        "id": str(user.id),
        "email": str(user.email),
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "max_active_bookings": user.max_active_bookings,
    }
