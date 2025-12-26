"""
Celery tasks for chat processing
"""

from datetime import datetime, timezone
from ..extensions import celery, db
from ..models import Job
from ..services.storage import storage
from ..services.cache import cache
from ..services.processor import process_chat, validate_whatsapp_format


@celery.task(bind=True, max_retries=2)
def process_chat_task(self, job_id: str):
    """
    Process WhatsApp chat file

    Args:
        job_id: UUID of the job to process
    """
    job = Job.query.get(job_id)
    if not job:
        return {"error": "Job not found"}

    try:
        # Mark as processing (single DB update at start)
        job.status = Job.STATUS_PROCESSING
        job.started_at = datetime.now(timezone.utc)
        job.current_step = "Starting..."
        db.session.commit()

        # Progress callback - Redis only (fast), skip DB during processing
        def update_progress(progress: int, step: str):
            # Only update Redis for real-time progress (skip DB round-trips)
            cache.set_job_progress(str(job_id), progress, step)

        update_progress(5, "Downloading file...")

        # Download file from R2
        file_content = storage.download_file(job.file_key)
        file_content = file_content.decode("utf-8")

        # Validate format
        is_valid, error_msg = validate_whatsapp_format(file_content)
        if not is_valid:
            raise ValueError(error_msg)

        # Process the chat with selected members filter
        result = process_chat(
            file_content=file_content,
            year=job.year_filter or 2025,
            selected_members=job.selected_members,
            progress_callback=update_progress,
        )

        # Extract metadata
        basic_stats = result.get("basic_stats", {})
        metadata = result.get("metadata", {})

        # Upload result to R2
        update_progress(98, "Saving results...")
        result_key = storage.upload_json(result, prefix="results", compress=True)

        # Cache result in Redis
        cache.set_job_result(str(job_id), result)

        # Mark completed
        job.status = Job.STATUS_COMPLETED
        job.progress = 100
        job.current_step = "Completed"
        job.result_key = result_key
        job.completed_at = datetime.now(timezone.utc)
        job.message_count = basic_stats.get("total_messages")
        job.participant_count = basic_stats.get("total_participants")
        job.group_name = metadata.get("group_name")
        db.session.commit()

        # Update status cache
        cache.set_job_status(str(job_id), job.to_status_dict())

        return {"status": "completed", "job_id": str(job_id)}

    except Exception as e:
        # Mark failed
        job.status = Job.STATUS_FAILED
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        # Update status cache
        cache.set_job_status(str(job_id), job.to_status_dict())

        # Optionally retry
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)

        return {"status": "failed", "error": str(e)}


@celery.task
def cleanup_expired_jobs():
    """
    Periodic task to cleanup expired jobs

    Schedule this with celery beat or external cron
    """
    now = datetime.now(timezone.utc)

    # Find expired jobs
    expired_jobs = Job.query.filter(
        Job.expires_at < now,
        Job.status.in_([Job.STATUS_COMPLETED, Job.STATUS_FAILED])
    ).all()

    deleted_count = 0

    for job in expired_jobs:
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
            cache.delete_job_cache(str(job.id))

            # Delete from database
            db.session.delete(job)
            deleted_count += 1

        except Exception as e:
            print(f"Error cleaning up job {job.id}: {e}")
            continue

    db.session.commit()

    return {"deleted": deleted_count}
