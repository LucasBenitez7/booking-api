from datetime import UTC, datetime, timedelta

import jwt

from booking.domain.exceptions.auth_errors import AuthenticationError


class JwtService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days

    def create_access_token(self, user_id: str) -> str:
        expire = datetime.now(tz=UTC) + timedelta(minutes=self._access_expire_minutes)
        payload = {
            "sub": user_id,
            "typ": "access",
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        expire = datetime.now(tz=UTC) + timedelta(days=self._refresh_expire_days)
        payload = {
            "sub": user_id,
            "typ": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> str:
        return self._decode_typed(token, expected_type="access")

    def decode_refresh_token(self, token: str) -> str:
        return self._decode_typed(token, expected_type="refresh")

    def _decode_typed(self, token: str, expected_type: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid or expired token") from exc
        if payload.get("typ") != expected_type:
            raise AuthenticationError("Invalid token type")
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise AuthenticationError("Invalid token subject")
        return sub
