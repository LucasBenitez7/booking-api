from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email
from booking.infrastructure.persistence.models.user_model import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=BookingId.from_string(model.id),
            email=Email(model.email),
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_admin=model.is_admin,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=str(entity.id),
            email=str(entity.email),
            full_name=entity.full_name,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_admin=entity.is_admin,
            created_at=entity.created_at,
        )
