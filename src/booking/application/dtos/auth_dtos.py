from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserDTO:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class LoginUserDTO:
    email: str
    password: str


@dataclass(frozen=True)
class RequestPasswordResetDTO:
    email: str


@dataclass(frozen=True)
class ConfirmPasswordResetDTO:
    token: str
    new_password: str
