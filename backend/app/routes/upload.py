"""
Upload route for WhatsApp chat files
"""

from flask import Blueprint, request, current_app
from ..extensions import db, limiter
from ..models import Job
from ..services.storage import storage
from ..services.cache import cache
from ..services.processor import quick_parse_participants
from ..utils.security import validate_file_upload, validate_year
from ..tasks.processing import process_chat_task

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_UPLOADS", "10/hour"))
def upload_chat():
    """
    Upload a WhatsApp chat export file and get participants

    ---
    Request:
        - file: The chat export .txt file (multipart/form-data)
        - year: (optional) Year to filter messages (default: 2025)

    Response:
        {
            "job_id": "uuid",
            "status": "awaiting_selection",
            "participants": ["Alice", "Bob", ...],
            "group_name": "Group Name"
        }
    """
    current_app.logger.info(f"Upload request received from {request.remote_addr}")

    # Check for file
    if "file" not in request.files:
        current_app.logger.warning("Upload rejected - No file in request")
        return {"error": "No file provided"}, 400

    file = request.files["file"]
    current_app.logger.info(f"File received: {file.filename}, content_type: {file.content_type}")

    # Validate file
    is_valid, error_msg = validate_file_upload(file)
    if not is_valid:
        current_app.logger.warning(f"Upload rejected - Validation failed: {error_msg}")
        return {"error": error_msg}, 400

    # Validate year
    year_param = request.form.get("year")
    is_valid, year, error_msg = validate_year(year_param)
    if not is_valid:
        return {"error": error_msg}, 400

    try:
        # Get file size and content
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        file_content = file.read().decode("utf-8")
        file.seek(0)

        # Quick parse to get participants (sync - fast operation)
        participants, group_name = quick_parse_participants(file_content)
        current_app.logger.info(f"Parsed {len(participants)} participants, group: {group_name}")

        if not participants:
            current_app.logger.warning("Upload rejected - No participants found after parsing")
            return {"error": "No participants found in chat"}, 400

        # Upload file to R2
        file_key = storage.upload_file(file, prefix="uploads")

        # Create job record with participants
        job = Job(
            status=Job.STATUS_AWAITING_SELECTION,
            original_filename=file.filename,
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

        current_app.logger.info(f"Upload successful - Job {job.id} created with {len(participants)} participants")

        return {
            "job_id": str(job.id),
            "status": job.status,
            "participants": participants,
            "group_name": group_name,
        }, 200

    except Exception as e:
        current_app.logger.error(f"Upload error: {e}", exc_info=True)
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
