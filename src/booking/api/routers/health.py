from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.deps import get_db_session, get_settings
from booking.infrastructure.config.settings import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> JSONResponse:
    return JSONResponse(
        {"status": "ok", "version": app_settings.app_version},
    )


@router.get("/health/ready")
async def health_ready(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> JSONResponse:
    await session.execute(text("SELECT 1"))
    return JSONResponse({"status": "ready"})
