"""Celery tasks for booking lifecycle events.

Each task creates its own DB session and runs async code via asyncio.run()
because Celery workers are synchronous by default.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from celery import Task

from booking.infrastructure.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_session_and_settings() -> tuple[object, object]:
    """Lazily import to avoid circular imports at module load time."""
    from booking.infrastructure.config.settings import get_settings
    from booking.infrastructure.persistence.database import get_session

    return get_session, get_settings()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[misc]
def send_booking_confirmation(self: Task, booking_id: str) -> None:
    """Send confirmation email/log after a booking is created."""

    async def _run() -> None:
        from booking.infrastructure.config.settings import get_settings
        from booking.infrastructure.notifications.logging_notification_service import (
            LoggingNotificationService,
        )
        from booking.infrastructure.persistence.database import get_session
        from booking.infrastructure.persistence.repositories.sqlalchemy_booking_repo import (
            SQLAlchemyBookingRepository,
        )
        from booking.infrastructure.persistence.repositories.sqlalchemy_user_repo import (
            SQLAlchemyUserRepository,
        )

        settings = get_settings()
        from booking.infrastructure.persistence.database import init_db

        init_db(settings.database_url)

        async for session in get_session():
            booking_repo = SQLAlchemyBookingRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            notification = LoggingNotificationService()

            from booking.domain.value_objects.booking_id import BookingId

            booking = await booking_repo.find_by_id(BookingId.from_string(booking_id))
            if booking is None:
                logger.warning(
                    "send_booking_confirmation: booking %s not found", booking_id
                )
                return

            user = await user_repo.find_by_id(booking.user_id)
            if user is None:
                logger.warning(
                    "send_booking_confirmation: user not found for booking %s",
                    booking_id,
                )
                return

            await notification.send_confirmation(booking, user)

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.exception("send_booking_confirmation failed for booking %s", booking_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[misc]
def send_booking_reminders(self: Task) -> None:
    """Send reminders for bookings starting within the configured window."""

    async def _run() -> None:
        from booking.infrastructure.config.settings import get_settings
        from booking.infrastructure.notifications.logging_notification_service import (
            LoggingNotificationService,
        )
        from booking.infrastructure.persistence.database import get_session, init_db
        from booking.infrastructure.persistence.repositories.sqlalchemy_booking_repo import (
            SQLAlchemyBookingRepository,
        )
        from booking.infrastructure.persistence.repositories.sqlalchemy_user_repo import (
            SQLAlchemyUserRepository,
        )

        settings = get_settings()
        init_db(settings.database_url)

        now = datetime.now(tz=UTC)
        reminder_cutoff = now + timedelta(hours=settings.reminder_hours_before)

        async for session in get_session():
            from booking.domain.value_objects.booking_status import BookingStatus

            booking_repo = SQLAlchemyBookingRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            notification = LoggingNotificationService()

            bookings = await booking_repo.find_all(status=BookingStatus.CONFIRMED)
            for booking in bookings:
                start = booking.time_slot.start
                if now <= start <= reminder_cutoff:
                    user = await user_repo.find_by_id(booking.user_id)
                    if user is not None:
                        await notification.send_reminder(booking, user)

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.exception("send_booking_reminders failed")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[misc]
def cleanup_expired_bookings(self: Task) -> None:
    """Mark confirmed bookings whose end time has passed as EXPIRED."""

    async def _run() -> None:
        from booking.infrastructure.config.settings import get_settings
        from booking.infrastructure.persistence.database import get_session, init_db
        from booking.infrastructure.persistence.repositories.sqlalchemy_booking_repo import (
            SQLAlchemyBookingRepository,
        )

        init_db(get_settings().database_url)

        now = datetime.now(tz=UTC)

        async for session in get_session():
            from booking.domain.value_objects.booking_status import BookingStatus

            booking_repo = SQLAlchemyBookingRepository(session)
            bookings = await booking_repo.find_all(status=BookingStatus.CONFIRMED)

            to_expire = [b for b in bookings if b.time_slot.end < now]
            for booking in to_expire:
                booking.expire()
                await booking_repo.update(booking)

            if to_expire:
                logger.info(
                    "cleanup_expired_bookings: expired %d bookings",
                    len(to_expire),
                )

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.exception("cleanup_expired_bookings failed")
        raise self.retry(exc=exc)
