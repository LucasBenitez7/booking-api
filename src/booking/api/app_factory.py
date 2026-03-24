import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

import redis.asyncio as redis
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from booking.api.exception_handlers import register_domain_exception_handlers
from booking.api.limiter import limiter
from booking.api.routers import admin as admin_router
from booking.api.routers import auth as auth_router
from booking.api.routers import bookings as bookings_router
from booking.api.routers import health as health_router
from booking.api.routers import spaces as spaces_router
from booking.domain.ports.availability_cache import AvailabilityCache
from booking.domain.ports.password_reset_token_store import PasswordResetTokenStore
from booking.infrastructure.auth.memory_password_reset_store import (
    MemoryPasswordResetStore,
)
from booking.infrastructure.auth.redis_password_reset_store import (
    RedisPasswordResetStore,
)
from booking.infrastructure.cache.memory_availability_cache import (
    MemoryAvailabilityCache,
)
from booking.infrastructure.cache.redis_availability_cache import RedisAvailabilityCache
from booking.infrastructure.config.settings import get_settings
from booking.infrastructure.notifications.logging_notification_service import (
    LoggingNotificationService,
)
from booking.infrastructure.persistence.database import close_db, init_db
from booking.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from booking.infrastructure.security.jwt_service import JwtService


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _configure_structlog()
    settings = get_settings()
    init_db(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )

    jwt_service = JwtService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expire_days=settings.jwt_refresh_token_expire_days,
    )
    password_hasher = BcryptPasswordHasher()
    notification_service = LoggingNotificationService()

    reset_store: PasswordResetTokenStore
    availability_cache: AvailabilityCache
    redis_client: redis.Redis | None = None
    if settings.redis_url:
        redis_client = cast(
            redis.Redis,
            redis.from_url(  # type: ignore[no-untyped-call]
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            ),
        )
        reset_store = RedisPasswordResetStore(redis_client)
        availability_cache = RedisAvailabilityCache(redis_client)
    else:
        reset_store = MemoryPasswordResetStore()
        availability_cache = MemoryAvailabilityCache()

    app.state.settings = settings
    app.state.jwt_service = jwt_service
    app.state.password_hasher = password_hasher
    app.state.password_reset_store = reset_store
    app.state.notification_service = notification_service
    app.state.availability_cache = availability_cache
    app.state.redis = redis_client

    yield

    await close_db()
    if redis_client is not None:
        await redis_client.aclose()
    get_settings.cache_clear()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="BookingAPI",
        description="REST API for space and room booking management",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

    register_domain_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    app.include_router(health_router.router)
    app.include_router(auth_router.router)
    app.include_router(spaces_router.router)
    app.include_router(bookings_router.router)
    app.include_router(admin_router.router)

    return app
