def register_blueprints(app):
    """Register all blueprints"""
    from .health import health_bp
    from .upload import upload_bp
    from .stats import stats_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")
