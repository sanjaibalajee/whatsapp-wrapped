from flask import Blueprint, current_app
from ..extensions import db, redis_client

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "services": {
            "api": "ok",
            "database": "unknown",
            "redis": "unknown",
        },
    }

    # Check database
    try:
        db.session.execute(db.text("SELECT 1"))
        status["services"]["database"] = "ok"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis
    try:
        if redis_client:
            redis_client.ping()
            status["services"]["redis"] = "ok"
        else:
            status["services"]["redis"] = "not configured"
    except Exception as e:
        status["services"]["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"

    http_status = 200 if status["status"] == "healthy" else 503
    return status, http_status


@health_bp.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return {
        "name": "WhatsApp Wrapped API",
        "version": "0.1.0",
        "status": "running",
    }
