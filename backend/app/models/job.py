import uuid
from datetime import datetime, timezone
from ..extensions import db


class Job(db.Model):
    """Job model for tracking chat processing"""

    __tablename__ = "jobs"

    # Primary key
    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Status tracking
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )
    progress = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(100))

    # Participants (JSON arrays)
    participants = db.Column(db.JSON)  # All participants from chat
    selected_members = db.Column(db.JSON)  # User-selected members for analysis

    # File info
    original_filename = db.Column(db.String(255))
    file_key = db.Column(db.String(255))
    file_size = db.Column(db.Integer)

    # Processing params
    year_filter = db.Column(db.Integer)

    # Results
    result_key = db.Column(db.String(255))
    message_count = db.Column(db.Integer)
    participant_count = db.Column(db.Integer)
    group_name = db.Column(db.String(255))

    # Error handling
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    started_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    expires_at = db.Column(db.DateTime(timezone=True))

    # Client info
    client_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    # Status constants
    STATUS_PENDING = "pending"
    STATUS_AWAITING_SELECTION = "awaiting_selection"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "job_id": str(self.id),
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "year_filter": self.year_filter,
            "participants": self.participants,
            "selected_members": self.selected_members,
            "message_count": self.message_count,
            "participant_count": self.participant_count,
            "group_name": self.group_name,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def to_status_dict(self):
        """Convert to status-only dictionary"""
        return {
            "job_id": str(self.id),
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def update_progress(self, progress: int, step: str = None):
        """Update job progress"""
        self.progress = progress
        if step:
            self.current_step = step
        db.session.commit()

    def mark_processing(self):
        """Mark job as processing"""
        self.status = self.STATUS_PROCESSING
        self.started_at = datetime.now(timezone.utc)
        db.session.commit()

    def mark_completed(self, result_key: str, message_count: int = None,
                       participant_count: int = None, group_name: str = None):
        """Mark job as completed"""
        self.status = self.STATUS_COMPLETED
        self.progress = 100
        self.current_step = "Completed"
        self.result_key = result_key
        self.completed_at = datetime.now(timezone.utc)
        if message_count:
            self.message_count = message_count
        if participant_count:
            self.participant_count = participant_count
        if group_name:
            self.group_name = group_name
        db.session.commit()

    def mark_failed(self, error_message: str):
        """Mark job as failed"""
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)
        db.session.commit()

    def __repr__(self):
        return f"<Job {self.id} status={self.status}>"
