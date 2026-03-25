"""Generate postman/collection.json — run: uv run python scripts/generate_postman_collection.py"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _url(path: str, query: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    parts = [p for p in path.split("/") if p]
    raw = "{{base_url}}/" + "/".join(parts) if parts else "{{base_url}}"
    url: dict[str, Any] = {
        "raw": raw,
        "host": ["{{base_url}}"],
        "path": parts,
    }
    if query:
        url["query"] = [{"key": k, "value": v} for k, v in query]
        raw += "?" + "&".join(f"{k}={v}" for k, v in query)
        url["raw"] = raw
    return url


def _body(data: dict[str, Any]) -> dict[str, Any]:
    return {"mode": "raw", "raw": json.dumps(data, indent=2)}


def _bearer() -> dict[str, Any]:
    return {
        "type": "bearer",
        "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
    }


def _admin_bearer() -> dict[str, Any]:
    return {
        "type": "bearer",
        "bearer": [{"key": "token", "value": "{{admin_token}}", "type": "string"}],
    }


def _event(listen: str, lines: list[str]) -> dict[str, Any]:
    return {
        "listen": listen,
        "script": {"exec": lines, "type": "text/javascript"},
    }


def req(
    name: str,
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    query: list[tuple[str, str]] | None = None,
    auth: dict[str, Any] | None = None,
    prerequest: list[str] | None = None,
    tests: list[str] | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    headers: list[dict[str, str]] = []
    if body is not None:
        headers.append({"key": "Content-Type", "value": "application/json"})

    r: dict[str, Any] = {
        "name": name,
        "request": {
            "method": method,
            "header": headers,
            "url": _url(path, query),
        },
    }
    if auth is not None:
        r["request"]["auth"] = auth
    if body is not None:
        r["request"]["body"] = _body(body)
    if description:
        r["request"]["description"] = description

    events = []
    if prerequest:
        events.append(_event("prerequest", prerequest))
    if tests:
        events.append(_event("test", tests))
    if events:
        r["event"] = events
    return r


# ---------------------------------------------------------------------------
# Pre-request scripts
# ---------------------------------------------------------------------------

PR_BOOKING_TIMES = [
    "const start = new Date();",
    "start.setUTCDate(start.getUTCDate() + 3);",
    "start.setUTCHours(14, 0, 0, 0);",
    "const end = new Date(start);",
    "end.setUTCHours(16, 0, 0, 0);",
    'pm.environment.set("booking_start", start.toISOString());',
    'pm.environment.set("booking_end", end.toISOString());',
]

PR_PATCH_BOOKING = [
    "const start = new Date();",
    "start.setUTCDate(start.getUTCDate() + 4);",
    "start.setUTCHours(14, 0, 0, 0);",
    "const end = new Date(start);",
    "end.setUTCHours(16, 0, 0, 0);",
    'pm.environment.set("patch_start", start.toISOString());',
    'pm.environment.set("patch_end", end.toISOString());',
]

PR_AVAILABILITY = [
    "const start = new Date();",
    "start.setUTCDate(start.getUTCDate() + 3);",
    "start.setUTCHours(14, 0, 0, 0);",
    "const end = new Date(start);",
    "end.setUTCHours(15, 0, 0, 0);",
    'pm.environment.set("availability_start", start.toISOString());',
    'pm.environment.set("availability_end", end.toISOString());',
]

PR_REGISTER_USER = [
    "const ts = Date.now();",
    'pm.environment.set("register_email", "user-" + ts + "@example.com");',
]

# ---------------------------------------------------------------------------
# Collection items
# ---------------------------------------------------------------------------


def setup_folder() -> dict[str, Any]:
    return {
        "name": "0 — Setup",
        "description": "Run these two requests first. Reset wipes the DB, Seed creates admin + spaces and returns the admin token.",
        "item": [
            req(
                "Reset (wipe DB)",
                "DELETE",
                "/dev/reset",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('DB wiped', () => pm.expect(pm.response.json().message).to.include('clean'));",
                ],
                description="Deletes all rows from bookings, spaces and users. Safe to call multiple times.",
            ),
            req(
                "Seed (create admin + spaces)",
                "POST",
                "/dev/seed",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has access_token', () => pm.expect(pm.response.json().access_token).to.be.a('string'));",
                    "const j = pm.response.json();",
                    'pm.environment.set("admin_token", j.access_token);',
                    'pm.environment.set("admin_email", j.admin_email);',
                    'pm.environment.set("admin_password", j.admin_password);',
                    'pm.environment.set("user_email", j.user_email);',
                    'pm.environment.set("user_password", j.user_password);',
                ],
                description="Creates admin@booking-api.com (Admin1234!) + regular user + 3 spaces. Saves admin_token to environment.",
            ),
        ],
    }


def health_folder() -> dict[str, Any]:
    return {
        "name": "1 — Health",
        "item": [
            req(
                "Liveness",
                "GET",
                "/health",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Status ok', () => pm.expect(pm.response.json().status).to.eql('ok'));",
                ],
            ),
            req(
                "Readiness (DB check)",
                "GET",
                "/health/ready",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Status ready', () => pm.expect(pm.response.json().status).to.eql('ready'));",
                ],
            ),
        ],
    }


def auth_folder() -> dict[str, Any]:
    return {
        "name": "2 — Auth",
        "item": [
            req(
                "Login admin",
                "POST",
                "/auth/login",
                body={"email": "{{admin_email}}", "password": "{{admin_password}}"},
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has access_token', () => pm.expect(pm.response.json().access_token).to.be.a('string'));",
                    'pm.environment.set("admin_token", pm.response.json().access_token);',
                ],
                description="Refreshes admin_token. Run after Seed.",
            ),
            req(
                "Register regular user",
                "POST",
                "/auth/register",
                body={
                    "email": "{{register_email}}",
                    "password": "Test1234!",
                    "full_name": "Postman User",
                },
                prerequest=PR_REGISTER_USER,
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has access_token', () => pm.expect(pm.response.json().access_token).to.be.a('string'));",
                    "const j = pm.response.json();",
                    'pm.environment.set("access_token", j.access_token);',
                    'pm.environment.set("user_id", j.user.id);',
                    'pm.environment.set("user_email", j.user.email);',
                ],
                description="Pre-request generates unique email (user-<timestamp>@example.com). Saves access_token and user_id.",
            ),
            req(
                "Login regular user",
                "POST",
                "/auth/login",
                body={"email": "{{register_email}}", "password": "Test1234!"},
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    'pm.environment.set("access_token", pm.response.json().access_token);',
                ],
                description="Uses register_email (set by Register pre-request) and password Test1234!",
            ),
            req(
                "Refresh token",
                "POST",
                "/auth/refresh",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has new access_token', () => pm.expect(pm.response.json().access_token).to.be.a('string'));",
                ],
                description="Uses HttpOnly refresh cookie set by Login/Register. Cookie jar must be enabled in Postman (default on).",
            ),
            req(
                "Password reset — request",
                "POST",
                "/auth/password-reset/request",
                body={"email": "{{user_email}}"},
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Safe response (no email leak)', () => pm.expect(pm.response.json().detail).to.include('If the email'));",
                ],
            ),
            req(
                "Logout",
                "DELETE",
                "/auth/logout",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                ],
                description="Clears the refresh cookie. Run this last in the Auth folder — bookings use access_token.",
            ),
        ],
    }


def spaces_folder() -> dict[str, Any]:
    return {
        "name": "3 — Spaces (public)",
        "item": [
            req(
                "List spaces",
                "GET",
                "/spaces",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Returns array', () => pm.expect(pm.response.json()).to.be.an('array'));",
                    "pm.test('Has at least 1 space', () => pm.expect(pm.response.json().length).to.be.above(0));",
                    "const spaces = pm.response.json();",
                    'pm.environment.set("space_id", spaces[0].id);',
                ],
                description="Saves first space id to space_id.",
            ),
            req(
                "Get space by id",
                "GET",
                "/spaces/{{space_id}}",
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('ID matches', () => pm.expect(pm.response.json().id).to.eql(pm.environment.get('space_id')));",
                ],
            ),
            req(
                "Check availability",
                "GET",
                "/spaces/{{space_id}}/availability",
                query=[
                    ("start", "{{availability_start}}"),
                    ("end", "{{availability_end}}"),
                ],
                prerequest=PR_AVAILABILITY,
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has is_available field', () => pm.expect(pm.response.json()).to.have.property('is_available'));",
                    "pm.test('Slot is available', () => pm.expect(pm.response.json().is_available).to.be.true);",
                ],
                description="Pre-request sets start/end to +3 days 14:00-15:00 UTC. Calls cache on second run (same result, faster).",
            ),
        ],
    }


def bookings_folder() -> dict[str, Any]:
    return {
        "name": "4 — Bookings (user)",
        "auth": _bearer(),
        "item": [
            req(
                "Create booking",
                "POST",
                "/bookings",
                body={
                    "space_id": "{{space_id}}",
                    "start": "{{booking_start}}",
                    "end": "{{booking_end}}",
                    "notes": "Postman demo booking",
                },
                auth=_bearer(),
                prerequest=PR_BOOKING_TIMES,
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has id', () => pm.expect(pm.response.json().id).to.be.a('string'));",
                    "pm.test('Status is confirmed', () => pm.expect(pm.response.json().status).to.eql('confirmed'));",
                    'pm.environment.set("booking_id", pm.response.json().id);',
                ],
                description="Pre-request sets dates to +3 days 14:00-16:00 UTC (respects min_advance_minutes and opening hours).",
            ),
            req(
                "List my bookings",
                "GET",
                "/bookings",
                auth=_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Returns array', () => pm.expect(pm.response.json()).to.be.an('array'));",
                    "pm.test('Has at least 1 booking', () => pm.expect(pm.response.json().length).to.be.above(0));",
                ],
            ),
            req(
                "List my bookings (status=confirmed)",
                "GET",
                "/bookings",
                query=[("status", "confirmed")],
                auth=_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('All confirmed', () => pm.response.json().forEach(b => pm.expect(b.status).to.eql('confirmed')));",
                ],
            ),
            req(
                "Get booking by id",
                "GET",
                "/bookings/{{booking_id}}",
                auth=_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('ID matches', () => pm.expect(pm.response.json().id).to.eql(pm.environment.get('booking_id')));",
                ],
            ),
            req(
                "Update booking",
                "PATCH",
                "/bookings/{{booking_id}}",
                body={
                    "start": "{{patch_start}}",
                    "end": "{{patch_end}}",
                    "notes": "Updated via Postman",
                },
                auth=_bearer(),
                prerequest=PR_PATCH_BOOKING,
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Notes updated', () => pm.expect(pm.response.json().notes).to.eql('Updated via Postman'));",
                ],
            ),
            req(
                "Cancel booking",
                "DELETE",
                "/bookings/{{booking_id}}",
                query=[("reason", "postman test")],
                auth=_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Status is cancelled', () => pm.expect(pm.response.json().status).to.eql('cancelled'));",
                ],
            ),
            req(
                "Get booking after cancel (status check)",
                "GET",
                "/bookings/{{booking_id}}",
                auth=_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Booking is cancelled', () => pm.expect(pm.response.json().status).to.eql('cancelled'));",
                ],
            ),
            req(
                "Unauthorized access (no token — expect 401)",
                "GET",
                "/bookings",
                auth={"type": "noauth"},
                tests=[
                    "pm.test('Status 401 without token', () => pm.response.to.have.status(401));",
                ],
                description="Verifies that the endpoint rejects unauthenticated requests.",
            ),
        ],
    }


def admin_folder() -> dict[str, Any]:
    return {
        "name": "5 — Admin",
        "auth": _admin_bearer(),
        "item": [
            req(
                "Create space",
                "POST",
                "/admin/spaces",
                body={
                    "name": "Postman Space",
                    "description": "Created via Postman collection",
                    "capacity": 6,
                    "price_per_hour": 30.0,
                },
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Has id', () => pm.expect(pm.response.json().id).to.be.a('string'));",
                    "pm.test('Name matches', () => pm.expect(pm.response.json().name).to.eql('Postman Space'));",
                    'pm.environment.set("admin_space_id", pm.response.json().id);',
                ],
            ),
            req(
                "Update space",
                "PATCH",
                "/admin/spaces/{{admin_space_id}}",
                body={"description": "Updated by admin via Postman"},
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Description updated', () => pm.expect(pm.response.json().description).to.eql('Updated by admin via Postman'));",
                ],
            ),
            req(
                "List all spaces (incl. inactive)",
                "GET",
                "/admin/spaces",
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Returns array', () => pm.expect(pm.response.json()).to.be.an('array'));",
                ],
            ),
            req(
                "List all bookings",
                "GET",
                "/admin/bookings",
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('Returns array', () => pm.expect(pm.response.json()).to.be.an('array'));",
                ],
            ),
            req(
                "List all bookings (status=cancelled)",
                "GET",
                "/admin/bookings",
                query=[("status", "cancelled")],
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('All cancelled', () => pm.response.json().forEach(b => pm.expect(b.status).to.eql('cancelled')));",
                ],
            ),
            req(
                "Update user (set max_active_bookings)",
                "PATCH",
                "/admin/users/{{user_id}}",
                body={"max_active_bookings": 10},
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                    "pm.test('max_active_bookings updated', () => pm.expect(pm.response.json().max_active_bookings).to.eql(10));",
                ],
            ),
            req(
                "Non-admin blocked (expect 403)",
                "GET",
                "/admin/bookings",
                auth=_bearer(),
                tests=[
                    "pm.test('Status 403 for non-admin', () => pm.response.to.have.status(403));",
                ],
                description="Uses regular user token — verifies admin-only enforcement.",
            ),
            req(
                "Deactivate space",
                "DELETE",
                "/admin/spaces/{{admin_space_id}}",
                auth=_admin_bearer(),
                tests=[
                    "pm.test('Status 200', () => pm.response.to.have.status(200));",
                ],
            ),
        ],
    }


def main() -> None:
    collection: dict[str, Any] = {
        "info": {
            "_postman_id": "c4d8f1a2-7b3e-4c9d-8f1a-2e6d9b0c4a5f",
            "name": "BookingAPI",
            "description": (
                "Full API collection for BookingAPI.\n\n"
                "**Quick start:**\n"
                "1. Import `postman/environment.json` and select **BookingAPI — Local**.\n"
                "2. Run **0 — Setup / Reset** to wipe the DB.\n"
                "3. Run **0 — Setup / Seed** — creates admin + spaces, saves `admin_token`.\n"
                "4. Run folders in order: Health → Auth → Spaces → Bookings → Admin.\n\n"
                "All tokens and IDs are saved automatically by test scripts. No manual steps required.\n\n"
                "**Newman (CLI):**\n"
                "```\nnewman run postman/collection.json -e postman/environment.json\n```"
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            setup_folder(),
            health_folder(),
            auth_folder(),
            spaces_folder(),
            bookings_folder(),
            admin_folder(),
        ],
    }

    out = Path(__file__).resolve().parent.parent / "postman" / "collection.json"
    out.write_text(json.dumps(collection, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
