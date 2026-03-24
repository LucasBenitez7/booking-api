# Contributing to BookingAPI

---

## Development workflow

### 1. Branch from `development`

All feature work starts from the `development` branch, not from `main`.

```bash
git checkout development
git pull origin development
git checkout -b feat/your-feature-name
```

`main` receives merges from `development` only when a release is ready. Direct pushes to `main` are not allowed.

### 2. Make your changes

Follow the code standards below. Run linters and tests before pushing.

```bash
# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/

# Unit tests
uv run pytest tests/unit/

# Security scan
uv run bandit -r src/ -c pyproject.toml
```

All four must pass before opening a PR. CI will enforce them too.

### 3. Open a PR against `development`

- PR title must follow Conventional Commits format (see below)
- CI must be green
- No self-merging

---

## Conventional Commits

Every commit message must follow this format:

```
<type>(<scope>): <short description>
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructure, no behavior change |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Maintenance, dependency updates |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvements |

### Scopes

Use the layer or module affected:

`domain` · `application` · `api` · `auth` · `bookings` · `spaces` · `admin` · `workers` · `cache` · `deps` · `k8s` · `ci`

### Examples

```
feat(bookings): add create booking endpoint
fix(auth): resolve token expiration on refresh
refactor(domain): extract Space.validate_cancellation method
test(application): add unit tests for RegisterUserUseCase
ci(github): pin trivy-action to v0.35.0
chore(deps): update fastapi to 0.115
```

---

## Code standards

### Architecture rules (non-negotiable)

- `domain/` has **zero external dependencies** — no FastAPI, no SQLAlchemy, no Pydantic
- `application/` has **no HTTP imports** — no FastAPI
- Ports are defined in `domain/ports/` as `Protocol` interfaces
- Infrastructure adapters implement ports — never the reverse
- SQLAlchemy models and domain entities are always separate classes connected by mappers

### Python style

- Python 3.12+ syntax — use `X | Y` unions, `match`, etc.
- Full type hints on every function and method
- `mypy --strict` must pass — no `type: ignore` unless absolutely necessary and explained in a comment
- `async def` for all I/O operations
- Pydantic v2 for HTTP schemas and settings only — domain DTOs use plain `dataclasses`
- Absolute imports always: `from booking.domain.entities.booking import Booking`

### Tests

- Unit tests live in `tests/unit/` and use mocks for all external dependencies
- Integration tests live in `tests/integration/` and require a running PostgreSQL + Redis
- Domain and application layer unit test coverage must stay at or above **80%**

---

## Running the project locally

See [README.md](README.md#local-setup) for full setup instructions.

Quick reference:

```bash
# Install all dependencies including dev extras
uv sync --extra dev

# Run services
docker-compose up

# Apply migrations
uv run alembic upgrade head

# Run the API in development mode
uv run uvicorn booking.api.main:app --reload

# Run a Celery worker (separate terminal)
uv run celery -A booking.infrastructure.workers.celery_app.celery_app worker --loglevel=info
```
