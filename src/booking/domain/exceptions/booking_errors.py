from booking.domain.exceptions.domain_exception import DomainException
from booking.domain.value_objects.booking_status import BookingStatus


class BookingConflictError(DomainException):
    def __init__(self, space_id: str, start: str, end: str) -> None:
        self.space_id = space_id
        self.start = start
        self.end = end
        super().__init__(
            f"Booking conflict for space '{space_id}' between {start} and {end}"
        )


class SpaceNotFoundError(DomainException):
    def __init__(self, space_id: str) -> None:
        self.space_id = space_id
        super().__init__(f"Space '{space_id}' not found")


class InvalidTimeSlotError(DomainException):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid time slot: {reason}")


class BookingNotFoundError(DomainException):
    def __init__(self, booking_id: str) -> None:
        self.booking_id = booking_id
        super().__init__(f"Booking '{booking_id}' not found")


class UserNotFoundError(DomainException):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User '{user_id}' not found")


class InvalidBookingStatusFilterError(DomainException):
    def __init__(self, status: str) -> None:
        self.status = status
        allowed = ", ".join(f"'{s.value}'" for s in BookingStatus)
        super().__init__(
            f"Invalid booking status filter: '{status}'. Expected one of: {allowed}."
        )


class UnauthorizedError(DomainException):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Unauthorized: {reason}")


class MaxActiveBookingsExceededError(DomainException):
    def __init__(self, max_active: int) -> None:
        self.max_active = max_active
        super().__init__(
            f"Maximum number of active bookings ({max_active}) has been reached"
        )


class CancellationDeadlineError(DomainException):
    def __init__(self, deadline_hours: int) -> None:
        self.deadline_hours = deadline_hours
        super().__init__(
            f"Bookings cannot be cancelled less than {deadline_hours} hours before the start time"
        )
