"""
Upload route for WhatsApp chat files
"""

from flask import Blueprint, request, current_app
from ..extensions import db, limiter
from ..models import Job
from ..services.storage import storage
from ..services.cache import cache
from ..utils.security import validate_file_upload, validate_year
from ..tasks.processing import process_chat_task

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_UPLOADS", "10/hour"))
def upload_chat():
    """
    Upload a WhatsApp chat export file for processing

    ---
    Request:
        - file: The chat export .txt file (multipart/form-data)
        - year: (optional) Year to filter messages (default: 2025)

    Response:
        {
            "job_id": "uuid",
            "status": "pending",
            "message": "Processing started"
        }
    """
    # Check for file
    if "file" not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files["file"]

    # Validate file
    is_valid, error_msg = validate_file_upload(file)
    if not is_valid:
        return {"error": error_msg}, 400

    # Validate year
    year_param = request.form.get("year")
    is_valid, year, error_msg = validate_year(year_param)
    if not is_valid:
        return {"error": error_msg}, 400

    try:
        # Get file size before upload (file stream will be consumed)
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        # Upload file to R2
        file_key = storage.upload_file(file, prefix="uploads")

        # Create job record
        job = Job(
            original_filename=file.filename,
            file_key=file_key,
            file_size=file_size,
            year_filter=year,
            client_ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        )
        db.session.add(job)
        db.session.commit()

        # Cache initial status
        cache.set_job_status(str(job.id), job.to_status_dict())

        # Queue processing task
        process_chat_task.delay(str(job.id))

        return {
            "job_id": str(job.id),
            "status": job.status,
            "message": "Processing started",
        }, 202

    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return {"error": "Failed to process upload"}, 500
