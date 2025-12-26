"""
Celery worker entry point
Run with: celery -A celery_worker.celery worker --loglevel=info
"""

from app import create_app
from app.extensions import celery

# Create Flask app to initialize Celery with config
app = create_app()

# Push app context so Celery tasks have access to Flask app
app.app_context().push()

# Import tasks to register them
from app.tasks import processing  # noqa: F401, E402
