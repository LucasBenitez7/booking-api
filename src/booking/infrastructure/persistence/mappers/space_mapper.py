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
            created_at=entity.created_at,
        )
