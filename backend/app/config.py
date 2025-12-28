import os
import ssl
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Flask (not critical for stateless API, but Flask requires it)
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())

    # Database - convert to psycopg3 driver format
    _db_url = os.getenv("DATABASE_URL", "")
    if _db_url.startswith("postgresql://"):
        _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url or None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Redis
    REDIS_URL = os.getenv("REDIS_URL")

    # Cloudflare R2
    R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
    R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "whatsapp-wrapped")
    R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com" if R2_ACCOUNT_ID else None

    # App settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    RESULT_TTL_SECONDS = int(os.getenv("RESULT_TTL_SECONDS", "3600"))
    UPLOAD_TTL_SECONDS = int(os.getenv("UPLOAD_TTL_SECONDS", "7200"))

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    # Rate limiting
    RATELIMIT_STORAGE_URI = REDIS_URL
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "200/hour"
    RATE_LIMIT_UPLOADS = os.getenv("RATE_LIMIT_UPLOADS", "10/hour")
    RATE_LIMIT_STATUS = os.getenv("RATE_LIMIT_STATUS", "100/minute")
    # SSL options for Upstash Redis
    RATELIMIT_STORAGE_OPTIONS = {"ssl_cert_reqs": ssl.CERT_NONE} if REDIS_URL and REDIS_URL.startswith("rediss://") else {}

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Stricter settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    }


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get config based on FLASK_ENV"""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
