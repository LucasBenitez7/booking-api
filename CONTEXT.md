# BookingAPI — Project Context

## What this is
REST API for booking management (coworking spaces, meeting rooms, appointments).
Portfolio project — demonstrates hexagonal architecture, async Python, Kubernetes deployment.

## Stack
| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Package manager | uv |
| API | FastAPI (async) |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Cache / broker | Redis 7 |
| Background jobs | Celery + celery-beat |
| Auth | JWT (PyJWT) + bcrypt |
| Rate limiting | slowapi |
| Logging | structlog (JSON) |
| Linting | Ruff |
| Type checking | mypy strict |
| Testing | pytest + httpx + factory-boy |
| Containers | Docker + docker-compose |
| Orchestration | Kubernetes / k3s (Hetzner) |
| CI/CD | GitHub Actions → ECR → kubectl (ci.yml + security.yml) |

## Architecture — Hexagonal (Ports & Adapters)
Dependency rule: inner layers never import from outer layers.
```
infrastructure (FastAPI, SQLAlchemy, Redis, Celery)
  └── application (use cases — no HTTP, no DB)
        └── domain (entities, value objects, ports — pure Python)
```

Ports = Protocol interfaces defined in domain/ports/.
Adapters = Concrete implementations in infrastructure/.
SQLAlchemy models and domain entities are always separate classes connected by mappers.

## Key architecture decisions
- **Domain entities are pure Python** — no SQLAlchemy, no Pydantic, no FastAPI imports ever
- **DTOs in application layer use dataclasses**, not Pydantic (Pydantic is HTTP-only)
- **Refresh token in HttpOnly cookie** — access token 15min, refresh token 7 days
- **Availability cached in Redis** — TTL 5 minutes, invalidated on create/cancel/update booking
- **ORM models ≠ domain entities** — connected via mappers in infrastructure/persistence/mappers/
- **Bookings are created directly as CONFIRMED** — no PENDING state in normal flow
- **Business rules live in Space entity** — min/max duration, advance time, cancellation deadline, opening hours
- **User controls their own booking limit** — max_active_bookings field, default 5, configurable by admin

## Development phases
- [x] Phase 0 — Project setup (uv, Ruff, mypy, Docker, docker-compose, GitHub Actions)
- [x] Phase 1 — Domain and application layer (entities, value objects, use cases, tests)
- [x] Phase 2 — Database infrastructure (SQLAlchemy repos, Alembic migrations)
- [x] Phase 2b — Domain business rules (Space constraints, UpdateBooking, admin powers)
- [x] Phase 3 — HTTP API and authentication (FastAPI routes, JWT, middleware, password reset via email token)
- [x] Phase 4 — Cache and async workers (Redis availability cache, Celery tasks)
- [x] Phase 5 — Kubernetes deployment (k3s, HPA, GitHub Actions deploy + release tagging)
- [x] Phase 6 — Polish, documentation and release (README, ADRs, coverage badge, release-please)

---

## Current status

**Current phase:** 5 — Kubernetes deployment

**Completed:**
- Phase 0 — uv init, pyproject.toml, folder structure,
  Dockerfile, docker-compose, GitHub Actions CI, README
- Phase 1 — Full domain and application layer:
  - Value Objects: BookingId, BookingStatus, TimeSlot, Email
  - Domain Events: BookingCreated, BookingCancelled, BookingUpdated
  - Domain Exceptions: DomainException base + all domain errors
  - Entities: Booking, Space, User
  - Ports: BookingRepository, SpaceRepository, UserRepository, NotificationService
  - DTOs: booking_dtos.py, booking_response_dto.py
  - Use Cases: CreateBooking, CancelBooking, GetAvailability, ListUserBookings, UpdateBooking
  - API: exception_handlers.py (domain → HTTP status codes)
- Phase 2 — Database infrastructure:
  - SQLAlchemy models: UserModel, SpaceModel, BookingModel
  - Mappers: UserMapper, SpaceMapper, BookingMapper
  - Repositories: SQLAlchemyUserRepository, SQLAlchemySpaceRepository, SQLAlchemyBookingRepository
  - Alembic config + migrations (initial schema + new columns)
  - Async database session with NullPool for tests
  - Seed script with demo data
- Phase 2b — Domain business rules:
  - Bookings created directly as CONFIRMED — no PENDING state
  - ConfirmBookingUseCase removed
  - Space: min/max_duration_minutes, min_advance_minutes, cancellation_deadline_hours, opening_time, closing_time
  - User: max_active_bookings (default 5, configurable by admin)
  - Admin can cancel any booking (is_admin flag bypasses ownership check)
  - UpdateBookingUseCase + BookingUpdated domain event
  - 49 unit tests passing — Ruff clean — mypy strict clean
- Phase 3 — HTTP API and authentication:
  - `create_app()` + lifespan: DB init, optional Redis, JWT, password reset store (Redis or in-memory)
  - Ports: PasswordHasher (async), AuthTokenIssuer, PasswordResetTokenStore (domain)
  - Use cases: RegisterUser, LoginUser, RefreshAccessToken, RequestPasswordReset, ConfirmPasswordReset
  - Admin: CreateSpace, UpdateSpace, DeactivateSpace (not hard delete), ListAdminBookings, UpdateUserAdmin; GetBooking
  - Public spaces: ListSpacesUseCase + GetSpaceUseCase (no infra imports in router)
  - Routers: auth, spaces, bookings, admin, health; Pydantic schemas; deps + rate limits (slowapi)
  - Middleware: CORS, security headers, X-Request-ID + structlog JSON; refresh token HttpOnly cookie
  - CreateBooking: enforce `max_active_bookings` + `Space.validate_booking_slot`; UpdateBooking: space conflict check
  - `Space.validate_booking_slot`: duration + advance + opening/closing hours
  - `Space.validate_cancellation`: cancellation_deadline_hours (admins bypass)
  - `CancellationDeadlineError` → HTTP 422
  - `Booking.create()` / `Booking.reconstitute()`: factory methods — creation emits BookingCreated, rehydration does not
  - `GetBookingUseCase`: authorization based on `user.is_admin` from DB (not from DTO)
  - `PasswordHasher` methods are async — bcrypt runs in thread executor (non-blocking)
  - `MIN_PASSWORD_LENGTH` centralized in `domain/value_objects/password_policy.py`
  - `MemoryPasswordResetStore`: tokens now expire via `time.monotonic` TTL
  - BookingRepository: `find_all`, `count_active_by_user`
  - Integration tests: `/health`, `/health/ready` (HTTP); 70 tests total — Ruff clean — mypy strict clean

- Phase 4 — Cache and async workers:
  - Port `AvailabilityCache` (domain) + `RedisAvailabilityCache` + `MemoryAvailabilityCache` (infrastructure)
  - `GetAvailabilityUseCase` checks cache first (TTL 5min), stores result on miss
  - `CreateBookingUseCase`, `UpdateBookingUseCase`, `CancelBookingUseCase` invalidate cache on mutation
  - Celery app (`celery_app.py`) with JSON serializer, UTC timezone, single-prefetch
  - Tasks: `send_booking_confirmation`, `send_booking_reminders`, `cleanup_expired_bookings` (with retry logic)
  - Beat schedule: reminders every hour, cleanup every 30 minutes
  - `MemoryAvailabilityCache` fallback when Redis not configured (respects TTL via `time.monotonic`)
  - Tests: 76 passing — Ruff clean — mypy strict clean

- Phase 5 — Kubernetes deployment:
  - Namespace manifest (`k8s/namespace.yaml`)
  - API: Deployment (liveness `/health`, readiness `/health/ready`, zero-downtime RollingUpdate), Service (ClusterIP), HPA (min 2 / max 10, CPU 70% + memory 80%), Ingress (nginx + cert-manager TLS)
  - Worker: Deployment with `celery worker` command + liveness via `celery inspect ping`
  - Beat: Deployment with `replicas: 1` + `Recreate` strategy to prevent duplicate scheduled tasks
  - Redis: Deployment + ClusterIP Service, password from Secret, LRU eviction policy
  - Secrets: template file only (no real values committed) — injected via CI/CD
  - NetworkPolicy: API ← ingress-nginx only; worker/beat → redis + postgres only; redis ← api/worker/beat only
  - `deploy.yml`: build + Trivy CRITICAL scan + push to ECR + `kubectl set image` rolling update for all three deployments; staging on `development` push, production on `main` push
  - `release.yml`: release-please automatic versioning + CHANGELOG from conventional commits
  - `security.yml`: added Trivy container scan job uploading SARIF to GitHub Security tab

**Working on now:** — all phases complete —

**Pending in Phase 6:**
- README.md: architecture diagram (Mermaid), stack badges, endpoints summary, local setup guide
- ADRs (Architecture Decision Records): 3-4 key decisions documented
- `.env.example`: complete and up to date with all variables
- Coverage badge in README (pytest-cov now enforces **≥80%** on application + domain + selected infra — see `pyproject.toml` `[tool.coverage.run] omit`)
- `CONTRIBUTING.md`: update with current workflow (branches, commits, PR process)

**Phase 6 progress — tests:**
- 124 unit tests: Space entity rules, auth (register/login/refresh), GetBooking, admin spaces, list bookings/spaces, password reset, logging notification adapter
- Coverage gate: `cov-fail-under=80` with HTTP/DB/Celery/Redis adapters omitted from the metric (those layers are covered by integration tests or staging)


**Known decisions / blockers:**
- SQLAlchemy models and domain entities are always separate — connected via mappers
- Use asyncpg driver (postgresql+asyncpg://)
- No PENDING state — bookings go directly to CONFIRMED
- max_active_bookings lives in User entity, not in global settings
- Password reset: token in Redis with 30min TTL, single-use, no email enumeration