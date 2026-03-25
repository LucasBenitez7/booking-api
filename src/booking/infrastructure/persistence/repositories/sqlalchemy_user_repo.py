from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email
from booking.infrastructure.persistence.mappers.user_mapper import UserMapper
from booking.infrastructure.persistence.models.user_model import UserModel


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, user_id: BookingId) -> User | None:
        result = await self._session.get(UserModel, str(user_id))
        if result is None:
            return None
        return UserMapper.to_domain(result)

    async def find_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def update(self, user: User) -> None:
        model = UserMapper.to_model(user)
        await self._session.merge(model)
        await self._session.flush()
