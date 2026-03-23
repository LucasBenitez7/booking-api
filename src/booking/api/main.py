from fastapi import FastAPI

from booking.api.exception_handlers import register_domain_exception_handlers

app = FastAPI(
    title="BookingAPI",
    description="REST API for space and room booking management",
    version="0.1.0",
)
register_domain_exception_handlers(app)
