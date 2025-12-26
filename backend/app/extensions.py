import ssl
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
from celery import Celery

# Database
db = SQLAlchemy()

# CORS
cors = CORS()

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],
)

# Redis client (initialized in create_app)
redis_client: Redis | None = None

# Celery (initialized separately)
celery = Celery("whatsapp-wrapped")


def init_redis(app):
    """Initialize Redis client"""
    global redis_client
    redis_url = app.config.get("REDIS_URL")
    if redis_url:
        # Handle SSL for Upstash (rediss://)
        if redis_url.startswith("rediss://"):
            redis_client = Redis.from_url(
                redis_url,
                decode_responses=True,
                ssl_cert_reqs=ssl.CERT_NONE,  # Don't verify SSL certs (Upstash handles this)
            )
        else:
            redis_client = Redis.from_url(redis_url, decode_responses=True)
    return redis_client


def init_celery(app):
    """Initialize Celery with Flask app context"""
    broker_url = app.config["CELERY_BROKER_URL"]
    result_backend = app.config["CELERY_RESULT_BACKEND"]

    # Configure SSL for Upstash Redis (rediss://)
    broker_use_ssl = None
    backend_use_ssl = None
    if broker_url and broker_url.startswith("rediss://"):
        broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    if result_backend and result_backend.startswith("rediss://"):
        backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        broker_use_ssl=broker_use_ssl,
        redis_backend_use_ssl=backend_use_ssl,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes max per task
        worker_prefetch_multiplier=1,
        broker_connection_retry_on_startup=True,
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
