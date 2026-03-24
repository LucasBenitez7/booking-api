from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.booking import Booking
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot
from booking.infrastructure.persistence.mappers.booking_mapper import BookingMapper
from booking.infrastructure.persistence.models.booking_model import BookingModel


class SQLAlchemyBookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, booking: Booking) -> None:
        model = BookingMapper.to_model(booking)
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, booking_id: BookingId) -> Booking | None:
        result = await self._session.get(BookingModel, str(booking_id))
        if result is None:
            return None
        return BookingMapper.to_domain(result)

    async def find_by_user(
        self,
        user_id: BookingId,
        status: BookingStatus | None = None,
    ) -> list[Booking]:
        stmt = select(BookingModel).where(BookingModel.user_id == str(user_id))
        if status is not None:
            stmt = stmt.where(BookingModel.status == status.value)
        result = await self._session.execute(stmt)
        return [BookingMapper.to_domain(m) for m in result.scalars().all()]

    async def find_conflicts(
        self,
        space_id: BookingId,
        time_slot: TimeSlot,
        exclude_booking_id: BookingId | None = None,
    ) -> list[Booking]:
        stmt = select(BookingModel).where(
            and_(
                BookingModel.space_id == str(space_id),
                BookingModel.status.notin_(
                    [BookingStatus.CANCELLED.value, BookingStatus.EXPIRED.value]
                ),
                BookingModel.start < time_slot.end,
                BookingModel.end > time_slot.start,
            )
        )
        if exclude_booking_id is not None:
            stmt = stmt.where(BookingModel.id != str(exclude_booking_id))
        result = await self._session.execute(stmt)
        return [BookingMapper.to_domain(m) for m in result.scalars().all()]

    async def update(self, booking: Booking) -> None:
        model = BookingMapper.to_model(booking)
        await self._session.merge(model)
        await self._session.flush()

    async def find_all(
        self,
        status: BookingStatus | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[Booking]:
        stmt = select(BookingModel).order_by(BookingModel.start.desc())
        if status is not None:
            stmt = stmt.where(BookingModel.status == status.value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [BookingMapper.to_domain(m) for m in result.scalars().all()]

    async def count_active_by_user(self, user_id: BookingId) -> int:
        stmt = (
            select(func.count())
            .select_from(BookingModel)
            .where(
                BookingModel.user_id == str(user_id),
                BookingModel.status == BookingStatus.CONFIRMED.value,
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
