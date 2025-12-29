"""
Upload route for WhatsApp chat files
"""

from flask import Blueprint, request, current_app
from ..extensions import db, limiter
from ..models import Job
from ..services.storage import storage
from ..services.cache import cache
from ..services.processor import quick_parse_participants
from ..utils.security import validate_file_content, validate_year
from ..tasks.processing import process_chat_task

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload/presign", methods=["GET"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_UPLOADS", "10/hour"))
def get_presigned_url():
    """
    Get a presigned URL for direct upload to R2

    ---
    Response:
        {
            "upload_url": "https://...",
            "file_key": "uploads/uuid.txt",
            "max_size_mb": 20,
            "expires_in": 3600
        }
    """
    current_app.logger.info(f"Presign request from {request.remote_addr}")

    try:
        max_size = current_app.config.get("MAX_FILE_SIZE_MB", 20)
        upload_url, file_key, max_size_mb = storage.generate_presigned_upload_url(
            prefix="uploads",
            expires_in=3600,
            max_size_mb=max_size,
        )

        return {
            "upload_url": upload_url,
            "file_key": file_key,
            "max_size_mb": max_size_mb,
            "expires_in": 3600,
        }, 200

    except Exception as e:
        current_app.logger.error(f"Presign error: {e}", exc_info=True)
        return {"error": "Failed to generate upload URL"}, 500


@upload_bp.route("/upload/confirm", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_UPLOADS", "10/hour"))
def confirm_upload():
    """
    Confirm upload and validate file after direct R2 upload

    ---
    Request (JSON):
        {
            "file_key": "uploads/uuid.txt",
            "filename": "chat.txt",
            "year": "2025"
        }

    Response:
        {
            "job_id": "uuid",
            "status": "awaiting_selection",
            "participants": ["Alice", "Bob", ...],
            "group_name": "Group Name"
        }
    """
    data = request.get_json()

    if not data:
        return {"error": "JSON body required"}, 400

    file_key = data.get("file_key")
    filename = data.get("filename", "chat.txt")

    if not file_key:
        return {"error": "file_key is required"}, 400

    # Validate year
    year_param = data.get("year")
    is_valid, year, error_msg = validate_year(year_param)
    if not is_valid:
        return {"error": error_msg}, 400

    current_app.logger.info(f"Confirm upload for {file_key} from {request.remote_addr}")

    try:
        # Check file exists in R2
        if not storage.file_exists(file_key):
            return {"error": "File not found. Upload may have failed."}, 404

        # Get file size
        file_size = storage.get_file_size(file_key)
        max_size = current_app.config.get("MAX_FILE_SIZE_MB", 20) * 1024 * 1024

        if file_size > max_size:
            storage.delete_file(file_key)
            return {"error": f"File too large. Maximum size is {max_size // (1024*1024)}MB"}, 400

        # Download and validate content
        file_content_bytes = storage.download_file(file_key)

        try:
            file_content = file_content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            storage.delete_file(file_key)
            return {"error": "Invalid file encoding. Please export chat as text file."}, 400

        # Validate file content
        is_valid, error_msg = validate_file_content(file_content)
        if not is_valid:
            storage.delete_file(file_key)
            current_app.logger.warning(f"Upload rejected - Validation failed: {error_msg}")
            return {"error": error_msg}, 400

        # Quick parse to get participants
        participants, group_name = quick_parse_participants(file_content)
        current_app.logger.info(f"Parsed {len(participants)} participants, group: {group_name}")

        if not participants:
            storage.delete_file(file_key)
            current_app.logger.warning("Upload rejected - No participants found after parsing")
            return {"error": "No participants found in chat. Please ensure this is a WhatsApp chat export."}, 400

        # Create job record with participants
        job = Job(
            status=Job.STATUS_AWAITING_SELECTION,
            original_filename=filename,
            file_key=file_key,
            file_size=file_size,
            year_filter=year,
            participants=participants,
            group_name=group_name,
            client_ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        )
        db.session.add(job)
        db.session.commit()

        # Cache initial status
        cache.set_job_status(str(job.id), job.to_status_dict())

        current_app.logger.info(f"Upload confirmed - Job {job.id} created with {len(participants)} participants")

        return {
            "job_id": str(job.id),
            "status": job.status,
            "participants": participants,
            "group_name": group_name,
        }, 200

    except Exception as e:
        current_app.logger.error(f"Confirm upload error: {e}", exc_info=True)
        # Try to clean up the file
        try:
            storage.delete_file(file_key)
        except Exception:
            pass
        return {"error": "Failed to process upload"}, 500


@upload_bp.route("/analyze", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_UPLOADS", "10/hour"))
def analyze_chat():
    """
    Start analysis for selected members

    ---
    Request (JSON):
        {
            "job_id": "uuid",
            "selected_members": ["Alice", "Bob"]
        }

    Response:
        {
            "job_id": "uuid",
            "status": "processing",
            "message": "Analysis started"
        }
    """
    data = request.get_json()

    if not data:
        return {"error": "JSON body required"}, 400

    job_id = data.get("job_id")
    selected_members = data.get("selected_members")

    if not job_id:
        return {"error": "job_id is required"}, 400

    if not selected_members or not isinstance(selected_members, list):
        return {"error": "selected_members must be a non-empty list"}, 400

    # Get job
    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}, 404

    if job.status != Job.STATUS_AWAITING_SELECTION:
        return {"error": f"Job is not awaiting selection (status: {job.status})"}, 400

    # Validate selected members are in participants
    invalid_members = set(selected_members) - set(job.participants or [])
    if invalid_members:
        return {"error": f"Invalid members: {list(invalid_members)}"}, 400

    try:
        # Update job with selected members
        job.selected_members = selected_members
        job.status = Job.STATUS_PENDING
        db.session.commit()

        # Cache updated status
        cache.set_job_status(str(job.id), job.to_status_dict())

        # Queue processing task
        process_chat_task.delay(str(job.id))

        return {
            "job_id": str(job.id),
            "status": job.status,
            "message": "Analysis started",
        }, 202

    except Exception as e:
        current_app.logger.error(f"Analyze error: {e}")
        return {"error": "Failed to start analysis"}, 500
