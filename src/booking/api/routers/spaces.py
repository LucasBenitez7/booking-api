from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from booking.api.deps import (
    get_get_availability_use_case,
    get_get_space_use_case,
    get_list_spaces_use_case,
)
from booking.api.schemas.space_schemas import SpacePublic
from booking.application.dtos.booking_dtos import GetAvailabilityDTO
from booking.application.use_cases.get_availability import GetAvailabilityUseCase
from booking.application.use_cases.list_spaces import GetSpaceUseCase, ListSpacesUseCase
from booking.domain.entities.space import Space

router = APIRouter(prefix="/spaces", tags=["spaces"])


def _space_to_public(space: Space) -> SpacePublic:
    return SpacePublic(
        id=str(space.id),
        name=space.name,
        description=space.description,
        capacity=space.capacity,
        price_per_hour=space.price_per_hour,
        is_active=space.is_active,
        min_duration_minutes=space.min_duration_minutes,
        max_duration_minutes=space.max_duration_minutes,
        min_advance_minutes=space.min_advance_minutes,
        cancellation_deadline_hours=space.cancellation_deadline_hours,
        opening_time=space.opening_time,
        closing_time=space.closing_time,
        created_at=space.created_at,
    )


@router.get("", response_model=list[SpacePublic])
async def list_spaces(
    use_case: Annotated[ListSpacesUseCase, Depends(get_list_spaces_use_case)],
) -> list[SpacePublic]:
    spaces = await use_case.execute()
    return [_space_to_public(s) for s in spaces]


@router.get("/{space_id}/availability")
async def get_space_availability(
    space_id: str,
    start: datetime,
    end: datetime,
    use_case: Annotated[GetAvailabilityUseCase, Depends(get_get_availability_use_case)],
) -> dict[str, object]:
    result = await use_case.execute(
        GetAvailabilityDTO(
            space_id=space_id,
            start=start,
            end=end,
        )
    )
    return {
        "space_id": result.space_id,
        "start": result.start,
        "end": result.end,
        "is_available": result.is_available,
        "conflicting_slots": result.conflicting_slots,
    }


@router.get("/{space_id}", response_model=SpacePublic)
async def get_space(
    space_id: str,
    use_case: Annotated[GetSpaceUseCase, Depends(get_get_space_use_case)],
) -> SpacePublic:
    space = await use_case.execute(space_id)
    return _space_to_public(space)
