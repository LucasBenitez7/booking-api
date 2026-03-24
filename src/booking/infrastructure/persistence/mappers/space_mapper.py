from booking.domain.entities.space import Space
from booking.domain.value_objects.booking_id import BookingId
from booking.infrastructure.persistence.models.space_model import SpaceModel


class SpaceMapper:
    @staticmethod
    def to_domain(model: SpaceModel) -> Space:
        return Space(
            id=BookingId.from_string(model.id),
            name=model.name,
            description=model.description,
            capacity=model.capacity,
            price_per_hour=model.price_per_hour,
            is_active=model.is_active,
            min_duration_minutes=model.min_duration_minutes,
            max_duration_minutes=model.max_duration_minutes,
            min_advance_minutes=model.min_advance_minutes,
            cancellation_deadline_hours=model.cancellation_deadline_hours,
            opening_time=model.opening_time,
            closing_time=model.closing_time,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Space) -> SpaceModel:
        return SpaceModel(
            id=str(entity.id),
            name=entity.name,
            description=entity.description,
            capacity=entity.capacity,
            price_per_hour=entity.price_per_hour,
            is_active=entity.is_active,
            min_duration_minutes=entity.min_duration_minutes,
            max_duration_minutes=entity.max_duration_minutes,
            min_advance_minutes=entity.min_advance_minutes,
            cancellation_deadline_hours=entity.cancellation_deadline_hours,
            opening_time=entity.opening_time,
            closing_time=entity.closing_time,
            created_at=entity.created_at,
        )
