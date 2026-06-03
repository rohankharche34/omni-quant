from celery import Celery
import os

redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery = Celery("omniquant", broker=redis_url, backend=redis_url)

# Load tasks
celery.autodiscover_tasks(['ml.tasks'])
