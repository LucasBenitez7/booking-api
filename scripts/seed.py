import asyncio
import os
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot
from booking.infrastructure.persistence.mappers.booking_mapper import BookingMapper
from booking.infrastructure.persistence.mappers.space_mapper import SpaceMapper
from booking.infrastructure.persistence.mappers.user_mapper import UserMapper


async def seed(session: AsyncSession) -> None:
    # Users
    admin = User(
        id=BookingId.generate(),
        email=Email("admin@booking-api.com"),
        full_name="Admin User",
        hashed_password="$2b$12$hashed_password_placeholder",
        is_active=True,
        is_admin=True,
    )
    user1 = User(
        id=BookingId.generate(),
        email=Email("lucas@booking-api.com"),
        full_name="Lucas Benítez",
        hashed_password="$2b$12$hashed_password_placeholder",
        is_active=True,
        is_admin=False,
    )

    # Spaces
    space1 = Space(
        id=BookingId.generate(),
        name="Sala de Reuniones A",
        description="Sala principal con capacidad para 10 personas y proyector.",
        capacity=10,
        price_per_hour=25.0,
    )
    space2 = Space(
        id=BookingId.generate(),
        name="Oficina Privada B",
        description="Oficina privada con escritorio y silla ergonómica.",
        capacity=2,
        price_per_hour=15.0,
    )
    space3 = Space(
        id=BookingId.generate(),
        name="Coworking Open Space",
        description="Espacio abierto con 20 puestos de trabajo.",
        capacity=20,
        price_per_hour=10.0,
    )

    # Bookings — fechas futuras
    now = datetime.now(tz=UTC)
    booking1 = Booking(
        id=BookingId.generate(),
        space_id=space1.id,
        user_id=user1.id,
        time_slot=TimeSlot(
            start=now + timedelta(days=1),
            end=now + timedelta(days=1, hours=2),
        ),
        status=BookingStatus.CONFIRMED,
        notes="Reunión de equipo",
    )
    booking2 = Booking(
        id=BookingId.generate(),
        space_id=space2.id,
        user_id=user1.id,
        time_slot=TimeSlot(
            start=now + timedelta(days=3),
            end=now + timedelta(days=3, hours=1),
        ),
        notes="Trabajo remoto",
    )

    # Persist
    for user in [admin, user1]:
        session.add(UserMapper.to_model(user))

    for space in [space1, space2, space3]:
        session.add(SpaceMapper.to_model(space))

    for booking in [booking1, booking2]:
        session.add(BookingMapper.to_model(booking))

    await session.commit()
    print("✅ Seed completado")
    print("   Usuarios: 2 (admin + user)")
    print("   Espacios: 3")
    print("   Reservas: 2")


async def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
