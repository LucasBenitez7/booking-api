from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.space import Space
from booking.domain.value_objects.booking_id import BookingId
from booking.infrastructure.persistence.mappers.space_mapper import SpaceMapper
from booking.infrastructure.persistence.models.space_model import SpaceModel


class SQLAlchemySpaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, space: Space) -> None:
        model = SpaceMapper.to_model(space)
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, space_id: BookingId) -> Space | None:
        result = await self._session.get(SpaceModel, str(space_id))
        if result is None:
            return None
        return SpaceMapper.to_domain(result)

    async def find_all(self, active_only: bool = True) -> list[Space]:
        stmt = select(SpaceModel)
        if active_only:
            stmt = stmt.where(SpaceModel.is_active == True)  # noqa: E712
        result = await self._session.execute(stmt)
        return [SpaceMapper.to_domain(m) for m in result.scalars().all()]

    async def update(self, space: Space) -> None:
        model = SpaceMapper.to_model(space)
        await self._session.merge(model)
        await self._session.flush()
