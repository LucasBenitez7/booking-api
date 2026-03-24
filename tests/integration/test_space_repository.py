import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.space import Space
from booking.domain.value_objects.booking_id import BookingId
from booking.infrastructure.persistence.repositories.sqlalchemy_space_repo import (
    SQLAlchemySpaceRepository,
)


def make_space(name: str = "Room A") -> Space:
    return Space(
        id=BookingId.generate(),
        name=name,
        description="Test room",
        capacity=10,
        price_per_hour=25.0,
    )


@pytest.mark.asyncio
async def test_save_and_find_space(db_session: AsyncSession) -> None:
    repo = SQLAlchemySpaceRepository(db_session)
    space = make_space()

    await repo.save(space)
    found = await repo.find_by_id(space.id)

    assert found is not None
    assert found.id == space.id
    assert found.name == space.name
    assert found.capacity == space.capacity


@pytest.mark.asyncio
async def test_find_space_not_found(db_session: AsyncSession) -> None:
    repo = SQLAlchemySpaceRepository(db_session)
    found = await repo.find_by_id(BookingId.generate())
    assert found is None


@pytest.mark.asyncio
async def test_find_all_active_spaces(db_session: AsyncSession) -> None:
    repo = SQLAlchemySpaceRepository(db_session)
    space1 = make_space("Room A")
    space2 = make_space("Room B")
    space3 = make_space("Room C")
    space3.deactivate()

    await repo.save(space1)
    await repo.save(space2)
    await repo.save(space3)

    active = await repo.find_all(active_only=True)
    all_spaces = await repo.find_all(active_only=False)

    active_ids = [s.id for s in active]
    assert space1.id in active_ids
    assert space2.id in active_ids
    assert space3.id not in active_ids
    assert len(all_spaces) >= 3


@pytest.mark.asyncio
async def test_update_space(db_session: AsyncSession) -> None:
    repo = SQLAlchemySpaceRepository(db_session)
    space = make_space()
    await repo.save(space)

    space.deactivate()
    await repo.update(space)

    found = await repo.find_by_id(space.id)
    assert found is not None
    assert found.is_active is False
