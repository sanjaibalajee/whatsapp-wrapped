from flask import Flask
from .config import get_config
from .extensions import db, cors, limiter, init_redis, init_celery


def create_app(config_class=None):
    """Application factory"""
    app = Flask(__name__)

    # Load config
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["ALLOWED_ORIGINS"]}},
        supports_credentials=False,
    )
    limiter.init_app(app)

    # Initialize Redis
    init_redis(app)

    # Initialize Celery
    init_celery(app)

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request", "message": str(error.description)}, 400

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "message": "Resource not found"}, 404

    @app.errorhandler(413)
    def file_too_large(error):
        max_size = app.config.get("MAX_FILE_SIZE_MB", 10)
        return {
            "error": "File too large",
            "message": f"Maximum file size is {max_size}MB",
        }, 413

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
        }, 429

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error", "message": "Something went wrong"}, 500
