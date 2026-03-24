from typing import Annotated

from fastapi import APIRouter, Depends, Query

from booking.api.deps import (
    get_cancel_booking_use_case,
    get_create_booking_use_case,
    get_current_user,
    get_get_booking_use_case,
    get_list_user_bookings_use_case,
    get_update_booking_use_case,
)
from booking.api.schemas.booking_schemas import (
    BookingPublic,
    CreateBookingBody,
    UpdateBookingBody,
)
from booking.application.dtos.booking_dtos import (
    CancelBookingDTO,
    CreateBookingDTO,
    GetBookingDTO,
    ListUserBookingsDTO,
    UpdateBookingDTO,
)
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.application.use_cases.cancel_booking import CancelBookingUseCase
from booking.application.use_cases.create_booking import CreateBookingUseCase
from booking.application.use_cases.get_booking import GetBookingUseCase
from booking.application.use_cases.list_user_bookings import ListUserBookingsUseCase
from booking.application.use_cases.update_booking import UpdateBookingUseCase
from booking.domain.entities.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])


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


@router.post("", response_model=BookingPublic)
async def create_booking(
    body: CreateBookingBody,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CreateBookingUseCase, Depends(get_create_booking_use_case)],
) -> BookingPublic:
    result = await use_case.execute(
        CreateBookingDTO(
            space_id=body.space_id,
            user_id=str(user.id),
            start=body.start,
            end=body.end,
            notes=body.notes,
        )
    )
    return _booking_to_public(result)


@router.get("", response_model=list[BookingPublic])
async def list_my_bookings(
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[
        ListUserBookingsUseCase, Depends(get_list_user_bookings_use_case)
    ],
    status: str | None = None,
) -> list[BookingPublic]:
    results = await use_case.execute(
        ListUserBookingsDTO(user_id=str(user.id), status=status),
    )
    return [_booking_to_public(r) for r in results]


@router.get("/{booking_id}", response_model=BookingPublic)
async def get_booking(
    booking_id: str,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetBookingUseCase, Depends(get_get_booking_use_case)],
) -> BookingPublic:
    result = await use_case.execute(
        GetBookingDTO(
            booking_id=booking_id,
            requesting_user_id=str(user.id),
        )
    )
    return _booking_to_public(result)


@router.patch("/{booking_id}", response_model=BookingPublic)
async def update_booking(
    booking_id: str,
    body: UpdateBookingBody,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateBookingUseCase, Depends(get_update_booking_use_case)],
) -> BookingPublic:
    result = await use_case.execute(
        UpdateBookingDTO(
            booking_id=booking_id,
            requesting_user_id=str(user.id),
            start=body.start,
            end=body.end,
            notes=body.notes,
        )
    )
    return _booking_to_public(result)


@router.delete("/{booking_id}", response_model=BookingPublic)
async def cancel_booking(
    booking_id: str,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CancelBookingUseCase, Depends(get_cancel_booking_use_case)],
    reason: str | None = Query(default=None),
) -> BookingPublic:
    result = await use_case.execute(
        CancelBookingDTO(
            booking_id=booking_id,
            cancelled_by=str(user.id),
            reason=reason,
        )
    )
    return _booking_to_public(result)
