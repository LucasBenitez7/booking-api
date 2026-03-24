from celery import Celery
from celery.signals import worker_init

from booking.infrastructure.config.settings import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    app = Celery(
        "booking",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["booking.infrastructure.workers.tasks.booking_tasks"],
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        worker_prefetch_multiplier=1,  # one task at a time per worker — safer for I/O tasks
    )
    return app


celery_app = create_celery_app()


@worker_init.connect
def _init_db_for_worker(**kwargs: object) -> None:
    """Initialise the SQLAlchemy engine once when the Celery worker boots.

    This avoids recreating the connection pool on every task invocation.
    init_db() is idempotent so calling it here and inside tasks is safe.
    """
    from booking.infrastructure.config.settings import get_settings
    from booking.infrastructure.persistence.database import init_db

    settings = get_settings()
    init_db(settings.database_url)
