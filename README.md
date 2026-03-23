# BookingAPI 🏢

> REST API for space and room booking management — coworking, meeting rooms, and consultations.

[![CI](https://github.com/LucasBenitez7/booking-api/actions/workflows/ci.yml/badge.svg)](https://github.com/LucasBenitez7/booking-api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Overview

BookingAPI is a production-grade REST API built with **Hexagonal Architecture (Ports & Adapters)**, designed to manage space reservations for coworking spaces, meeting rooms, and consultation slots.

## Stack

| Layer               | Technology                           |
| ------------------- | ------------------------------------ |
| **API**             | FastAPI + Pydantic v2                |
| **Database**        | PostgreSQL 16 + SQLAlchemy 2.0 async |
| **Migrations**      | Alembic                              |
| **Cache**           | Redis 7                              |
| **Background Jobs** | Celery + celery-beat                 |
| **Auth**            | PyJWT + passlib/bcrypt               |
| **Observability**   | structlog (JSON logs)                |
| **Testing**         | pytest + httpx + factory-boy         |
| **Linting**         | Ruff + mypy strict                   |
| **Deploy**          | Kubernetes (k3s) + GitHub Actions    |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                   │
│  (FastAPI routes, SQLAlchemy repos, Redis, Celery)  │
│                                                     │
│   ┌─────────────────────────────────────────────┐   │
│   │              APPLICATION                    │   │
│   │  (Use cases: CreateBooking, CancelBooking…) │   │
│   │                                             │   │
│   │   ┌───────────────────────────────────┐     │   │
│   │   │             DOMAIN                │     │   │
│   │   │  (Entities, Value Objects,        │     │   │
│   │   │   Domain Events, Port interfaces) │     │   │
│   │   └───────────────────────────────────┘     │   │
│   └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

The domain layer has **zero external dependencies** — no FastAPI, no SQLAlchemy. Everything connects through Protocol interfaces (Ports).

## Local Setup

### Prerequisites

- Docker + Docker Compose
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### Run locally

```bash
git clone https://github.com/LucasBenitez7/booking-api.git
cd booking-api
cp .env.example .env
docker-compose up
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Run tests

```bash
uv sync --extra dev
uv run pytest
```

## API Endpoints

| Method | Endpoint                    | Description                  |
| ------ | --------------------------- | ---------------------------- |
| POST   | `/auth/register`            | Register new user            |
| POST   | `/auth/login`               | Login → JWT tokens           |
| POST   | `/auth/refresh`             | Refresh access token         |
| GET    | `/spaces`                   | List spaces (paginated)      |
| GET    | `/spaces/{id}/availability` | Check availability           |
| POST   | `/bookings`                 | Create booking               |
| GET    | `/bookings`                 | List my bookings             |
| DELETE | `/bookings/{id}`            | Cancel booking               |
| GET    | `/health`                   | Liveness check               |
| GET    | `/health/ready`             | Readiness check (DB + Redis) |

## Project Structure

```
src/booking/
├── domain/          # Pure Python — no external dependencies
│   ├── entities/    # Booking, Space, User
│   ├── value_objects/
│   ├── events/
│   ├── exceptions/
│   └── ports/       # Protocol interfaces (contracts)
├── application/     # Use cases — orchestrates domain
├── infrastructure/  # Adapters — implements ports
│   ├── persistence/ # SQLAlchemy repositories
│   ├── cache/       # Redis
│   └── workers/     # Celery tasks
└── api/             # FastAPI layer
```

## License

[MIT](LICENSE)
