"""
Celery configuration for Tennis Team Website.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tennis_backend.settings')

# Create the Celery app
app = Celery('tennis_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Set up periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    'send-hourly-notifications': {
        'task': 'notifications.tasks.send_hourly_notifications',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour at minute 0
        'options': {'expires': 3600},  # Expire after 1 hour
    },
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'check-upcoming-matches': {
        'task': 'matches.tasks.check_upcoming_matches',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    'send-availability-reminders': {
        'task': 'matches.tasks.send_availability_reminders',
        'schedule': crontab(hour=18, minute=0),  # Daily at 6 PM
    },
}

# Configure result backend
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')

# Configure task serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Configure timezone
app.conf.timezone = 'UTC'

# Configure task time limits
app.conf.task_time_limit = 300  # 5 minutes
app.conf.task_soft_time_limit = 240  # 4 minutes

# Configure worker settings
app.conf.worker_prefetch_multiplier = 4
app.conf.worker_max_tasks_per_child = 1000
app.conf.worker_max_memory_per_child = 300000  # 300MB

# Configure result settings
app.conf.result_expires = 3600  # 1 hour
app.conf.result_cache_max = 1000


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')