from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from booking.domain.exceptions.booking_errors import (
    BookingConflictError,
    BookingNotFoundError,
    InvalidBookingStatusFilterError,
    InvalidTimeSlotError,
    SpaceNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
)
from booking.domain.exceptions.domain_exception import DomainException


def register_domain_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def handle_domain_exception(
        request: Request,
        exc: DomainException,
    ) -> JSONResponse:
        status_code = _http_status_for_domain_exception(exc)
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )


def _http_status_for_domain_exception(exc: DomainException) -> int:
    if isinstance(exc, BookingConflictError):
        return 409
    if isinstance(exc, (SpaceNotFoundError, BookingNotFoundError, UserNotFoundError)):
        return 404
    if isinstance(exc, (InvalidTimeSlotError, InvalidBookingStatusFilterError)):
        return 400
    if isinstance(exc, UnauthorizedError):
        return 403
    return 500
