"""
Gunicorn configuration
"""

import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Workers
workers = int(os.getenv("GUNICORN_WORKERS", "4"))
worker_class = "sync"
threads = 2

# Timeout (longer for file uploads)
timeout = 120
graceful_timeout = 30

# Keep-alive
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Process naming
proc_name = "whatsapp-wrapped-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

# Limits
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Restart workers after this many requests (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster worker startup
preload_app = True


def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_exit(server):
    """Called just before exiting Gunicorn."""
    pass


def worker_exit(server, worker):
    """Called when a worker exits."""
    pass
