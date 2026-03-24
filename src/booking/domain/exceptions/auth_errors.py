from booking.domain.exceptions.domain_exception import DomainException


class AuthenticationError(DomainException):
    """Invalid credentials or expired/invalid token."""

    def __init__(self, reason: str = "Could not validate credentials") -> None:
        self.reason = reason
        super().__init__(reason)


class EmailAlreadyRegisteredError(DomainException):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"An account with email '{email}' already exists")


class AdminRequiredError(DomainException):
    def __init__(self) -> None:
        super().__init__("Admin privileges required")


class InvalidPasswordResetTokenError(DomainException):
    def __init__(self) -> None:
        super().__init__("Invalid or expired password reset token")


class WeakPasswordError(DomainException):
    def __init__(self, min_length: int) -> None:
        self.min_length = min_length
        super().__init__(f"Password must be at least {min_length} characters")
