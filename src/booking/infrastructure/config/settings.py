from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field("production", alias="APP_ENV")
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = Field(
        ...,
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(10, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(20, alias="DATABASE_MAX_OVERFLOW")

    redis_url: str | None = Field(None, alias="REDIS_URL")
    celery_broker_url: str = Field(
        "redis://localhost:6379/0", alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        "redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND"
    )
    reminder_hours_before: int = Field(24, alias="REMINDER_HOURS_BEFORE")

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        15, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    refresh_token_cookie_name: str = "refresh_token"
    refresh_token_cookie_secure: bool = Field(
        False, alias="REFRESH_TOKEN_COOKIE_SECURE"
    )
    password_reset_token_ttl_seconds: int = 1800

    rate_limit_per_minute: int = Field(100, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_auth_per_minute: int = Field(10, alias="RATE_LIMIT_AUTH_PER_MINUTE")

    allowed_origins: str = Field(
        "http://localhost:3000,http://localhost:8000",
        alias="ALLOWED_ORIGINS",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, v: str | list[str]) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return v

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
