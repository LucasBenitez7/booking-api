import logging

from booking.domain.entities.booking import Booking
from booking.domain.entities.user import User

logger = logging.getLogger(__name__)


class LoggingNotificationService:
    async def send_confirmation(self, booking: Booking, user: User) -> None:
        logger.info(
            "booking_confirmation booking_id=%s user_id=%s",
            booking.id,
            user.id,
        )

    async def send_reminder(self, booking: Booking, user: User) -> None:
        logger.info(
            "booking_reminder booking_id=%s user_id=%s",
            booking.id,
            user.id,
        )

    async def send_cancellation(self, booking: Booking, user: User) -> None:
        logger.info(
            "booking_cancellation booking_id=%s user_id=%s",
            booking.id,
            user.id,
        )

    async def send_password_reset_email(self, email: str, reset_token: str) -> None:
        _ = reset_token  # never log tokens, even partially
        logger.info("password_reset_email email=%s", email)
