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
- **Availability cached in Redis** — TTL 5 minutes, invalidated on create/cancel booking
- **ORM models ≠ domain entities** — connected via mappers in infrastructure/persistence/mappers/

## Development phases
- [x] Phase 0 — Project setup (uv, Ruff, mypy, Docker, docker-compose, GitHub Actions)
- [ ] Phase 1 — Domain and application layer (entities, value objects, use cases, tests)
- [ ] Phase 2 — Database infrastructure (SQLAlchemy repos, Alembic migrations)
- [ ] Phase 3 — HTTP API and authentication (FastAPI routes, JWT, middleware)
- [ ] Phase 4 — Cache and async workers (Redis availability cache, Celery tasks)
- [ ] Phase 5 — Kubernetes deployment (k3s, HPA, GitHub Actions deploy + release tagging)
- [ ] Phase 6 — Polish, documentation and release (README, ADRs, coverage badge, release-please with release.yml )

---

## Current status

**Current phase:** 1 — Domain and application layer
**Completed:**
- Phase 0 — uv init, pyproject.toml, folder structure,
  Dockerfile, docker-compose, GitHub Actions CI, README
- Value Objects: BookingId, BookingStatus, TimeSlot, Email
- Domain Events: BookingCreated, BookingCancelled
- Domain Exceptions: DomainException base, BookingConflictError, 
  SpaceNotFoundError, UserNotFoundError, BookingNotFoundError,
  UnauthorizedError, InvalidTimeSlotError, InvalidBookingStatusFilterError
- Entities: Booking, Space, User
- Ports: BookingRepository, SpaceRepository, UserRepository, NotificationService
- DTOs: booking_dtos.py (CreateBookingDTO, CancelBookingDTO, 
  GetAvailabilityDTO, ListUserBookingsDTO, ConfirmBookingDTO,
  BookingResponseDTO, AvailabilityResponseDTO)
- Use Cases: CreateBooking, CancelBooking, GetAvailability, 
  ListUserBookings, ConfirmBooking

**Working on now:** —
**Pending in this phase:**
- Entities: Booking, Space, User
- Value Objects: TimeSlot, BookingStatus, Email, BookingId
- Domain Events: BookingCreated, BookingCancelled
- Domain Exceptions: BookingConflictError, SpaceNotFoundError
- Ports: BookingRepository, SpaceRepository, NotificationService
- Use Cases: CreateBooking, CancelBooking, GetAvailability, ListUserBookings
- Tests unitarios de todo lo anterior

**Known decisions / blockers:** none yet