"""Celery Beat periodic task schedule.

To start the beat scheduler:
    celery -A booking.infrastructure.workers.celery_app beat --loglevel=info
"""

from celery.schedules import crontab

from booking.infrastructure.workers.celery_app import celery_app

celery_app.conf.beat_schedule = {
    # Run every hour to send reminders for bookings starting within the next 24h
    "send-booking-reminders-hourly": {
        "task": "booking.infrastructure.workers.tasks.booking_tasks.send_booking_reminders",
        "schedule": crontab(minute=0),  # top of every hour
    },
    # Run every 30 minutes to cancel bookings whose end time has passed
    "cleanup-expired-bookings": {
        "task": "booking.infrastructure.workers.tasks.booking_tasks.cleanup_expired_bookings",
        "schedule": crontab(minute="*/30"),  # every 30 minutes
    },
}
