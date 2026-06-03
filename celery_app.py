from celery import Celery
import os

redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery = Celery("omniquant", broker=redis_url, backend=redis_url)

# Load tasks
celery.autodiscover_tasks(['ml.tasks'])

from celery.schedules import crontab

# Configure Scheduled Retraining (Priority 5)
celery.conf.beat_schedule = {
    'daily-retraining': {
        'task': 'ml.tasks.compute_predictions',
        # Run every day at midnight
        'schedule': crontab(hour=0, minute=0),
        'args': ('bitcoin', 1)
    },
}
