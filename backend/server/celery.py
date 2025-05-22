"""
Celery Configuration

This module configures Celery for background task processing,
including task scheduling and worker configuration.
"""


from __future__ import absolute_import, unicode_literals
import os
from dotenv import load_dotenv

load_dotenv()
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

app = Celery("backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all celery-related configs in Django settings must start with 'CELERY_'.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND
print("🐍 Broker from settings:", settings.CELERY_BROKER_URL)
# Set timezone
app.conf.timezone = "UTC"

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure beat schedule
app.conf.beat_schedule = {
    "cleanup-expired-contexts": {
        "task": "utils.tasks.cleanup_expired_redis_context",
        "schedule": crontab(minute=0),  # Run at the start of every hour
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    "generate-weekly-topic-transition-report": {
        "task": "server.tasks.generate_topic_transition_report",
        "schedule": crontab(
            minute=0, hour=1, day_of_week="monday"
        ),  # Run at 1 AM every Monday
        "args": (),
    },
}

# Configure task routing
app.conf.task_routes = {
    "utils.tasks.*": {"queue": "utils"},
    "services.tasks.*": {"queue": "services"},
    "default": {"queue": "default"},
}

# Configure task settings
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3540,  # 59 minutes
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    broker_connection_retry_on_startup=True,
)


@app.task(bind=True)
def debug_task(self):
    """Test task to verify Celery is working."""
    print(f"Request: {self.request!r}")
