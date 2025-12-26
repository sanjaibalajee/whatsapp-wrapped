"""
Stats retrieval routes
"""

from flask import Blueprint, current_app
from ..extensions import limiter
from ..models import Job
from ..services.storage import storage
from ..services.cache import cache
from ..utils.security import validate_uuid

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/jobs/<job_id>", methods=["GET"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_STATUS", "100/minute"))
def get_job_status(job_id: str):
    """
    Get job status and progress

    ---
    Response:
        {
            "job_id": "uuid",
            "status": "pending|processing|completed|failed",
            "progress": 0-100,
            "current_step": "Analyzing emojis...",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    # Validate UUID
    is_valid, error_msg = validate_uuid(job_id)
    if not is_valid:
        return {"error": error_msg}, 400

    # Try cache first
    cached_status = cache.get_job_status(job_id)
    if cached_status:
        # Also check for real-time progress
        progress = cache.get_job_progress(job_id)
        if progress:
            cached_status.update(progress)
        return cached_status, 200

    # Fall back to database
    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}, 404

    status = job.to_status_dict()

    # Cache it for next time
    cache.set_job_status(job_id, status)

    return status, 200


@stats_bp.route("/jobs/<job_id>/stats", methods=["GET"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_STATUS", "100/minute"))
def get_job_stats(job_id: str):
    """
    Get full stats for a completed job

    ---
    Response:
        {
            "job_id": "uuid",
            "status": "completed",
            "stats": { ... all stats ... },
            "metadata": { ... }
        }
    """
    # Validate UUID
    is_valid, error_msg = validate_uuid(job_id)
    if not is_valid:
        return {"error": error_msg}, 400

    # Get job
    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}, 404

    if job.status == Job.STATUS_PENDING:
        return {
            "job_id": job_id,
            "status": job.status,
            "message": "Job is pending",
        }, 202

    if job.status == Job.STATUS_PROCESSING:
        progress = cache.get_job_progress(job_id) or {}
        return {
            "job_id": job_id,
            "status": job.status,
            "progress": progress.get("progress", job.progress),
            "current_step": progress.get("current_step", job.current_step),
            "message": "Job is still processing",
        }, 202

    if job.status == Job.STATUS_FAILED:
        return {
            "job_id": job_id,
            "status": job.status,
            "error": job.error_message,
        }, 200

    # Job completed - get results
    # Try cache first
    cached_result = cache.get_job_result(job_id)
    if cached_result:
        return {
            "job_id": job_id,
            "status": job.status,
            "stats": cached_result,
            "metadata": {
                "message_count": job.message_count,
                "participant_count": job.participant_count,
                "group_name": job.group_name,
                "year": job.year_filter,
                "processing_time_ms": int(
                    (job.completed_at - job.started_at).total_seconds() * 1000
                ) if job.completed_at and job.started_at else None,
            },
        }, 200

    # Fall back to R2
    if not job.result_key:
        return {"error": "Results not available"}, 500

    try:
        result = storage.download_json(job.result_key)

        # Cache for next time
        cache.set_job_result(job_id, result)

        return {
            "job_id": job_id,
            "status": job.status,
            "stats": result,
            "metadata": {
                "message_count": job.message_count,
                "participant_count": job.participant_count,
                "group_name": job.group_name,
                "year": job.year_filter,
            },
        }, 200

    except Exception as e:
        current_app.logger.error(f"Error fetching results: {e}")
        return {"error": "Failed to retrieve results"}, 500


@stats_bp.route("/jobs/<job_id>/stats/<section>", methods=["GET"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_STATUS", "100/minute"))
def get_job_stats_section(job_id: str, section: str):
    """
    Get specific section of stats

    Available sections:
        - basic_stats
        - top_chatters
        - hourly_activity
        - daily_activity
        - emoji_stats
        - media_stats
        - word_stats
        - personality_tags
        - group_vibe
        - ... (any top-level key in stats)
    """
    # Validate UUID
    is_valid, error_msg = validate_uuid(job_id)
    if not is_valid:
        return {"error": error_msg}, 400

    # Get job
    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}, 404

    if job.status != Job.STATUS_COMPLETED:
        return {"error": f"Job status is {job.status}"}, 400

    # Try cache first
    cached_result = cache.get_job_result(job_id)
    if cached_result:
        if section not in cached_result:
            return {"error": f"Unknown section: {section}"}, 400
        return {
            "job_id": job_id,
            "section": section,
            "data": cached_result[section],
        }, 200

    # Fall back to R2
    if not job.result_key:
        return {"error": "Results not available"}, 500

    try:
        result = storage.download_json(job.result_key)

        # Cache full result
        cache.set_job_result(job_id, result)

        if section not in result:
            return {"error": f"Unknown section: {section}"}, 400

        return {
            "job_id": job_id,
            "section": section,
            "data": result[section],
        }, 200

    except Exception as e:
        current_app.logger.error(f"Error fetching results: {e}")
        return {"error": "Failed to retrieve results"}, 500


@stats_bp.route("/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id: str):
    """
    Delete a job and its associated data
    """
    # Validate UUID
    is_valid, error_msg = validate_uuid(job_id)
    if not is_valid:
        return {"error": error_msg}, 400

    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}, 404

    try:
        # Delete files from R2
        keys_to_delete = []
        if job.file_key:
            keys_to_delete.append(job.file_key)
        if job.result_key:
            keys_to_delete.append(job.result_key)

        if keys_to_delete:
            storage.delete_files(keys_to_delete)

        # Delete from cache
        cache.delete_job_cache(job_id)

        # Delete from database
        from ..extensions import db
        db.session.delete(job)
        db.session.commit()

        return {"message": "Job deleted successfully"}, 200

    except Exception as e:
        current_app.logger.error(f"Error deleting job: {e}")
        return {"error": "Failed to delete job"}, 500
