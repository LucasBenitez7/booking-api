from booking.domain.entities.booking import Booking
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot
from booking.infrastructure.persistence.models.booking_model import BookingModel


class BookingMapper:
    @staticmethod
    def to_domain(model: BookingModel) -> Booking:
        return Booking(
            id=BookingId.from_string(model.id),
            space_id=BookingId.from_string(model.space_id),
            user_id=BookingId.from_string(model.user_id),
            time_slot=TimeSlot(start=model.start, end=model.end),
            status=BookingStatus(model.status),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Booking) -> BookingModel:
        return BookingModel(
            id=str(entity.id),
            space_id=str(entity.space_id),
            user_id=str(entity.user_id),
            start=entity.time_slot.start,
            end=entity.time_slot.end,
            status=entity.status.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
