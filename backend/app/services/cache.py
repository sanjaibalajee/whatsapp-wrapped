import json
import gzip
import base64
from flask import current_app
from ..extensions import redis_client


class CacheService:
    """Redis cache service for job status and results"""

    # Key prefixes
    PREFIX_STATUS = "job:status:"
    PREFIX_RESULT = "job:result:"
    PREFIX_PROGRESS = "job:progress:"

    def __init__(self):
        pass

    @property
    def client(self):
        return redis_client

    @property
    def result_ttl(self):
        return current_app.config.get("RESULT_TTL_SECONDS", 3600)

    # Job status caching
    def set_job_status(self, job_id: str, status: dict, ttl: int = None):
        """Cache job status"""
        if not self.client:
            return

        key = f"{self.PREFIX_STATUS}{job_id}"
        ttl = ttl or self.result_ttl
        self.client.setex(key, ttl, json.dumps(status))

    def get_job_status(self, job_id: str) -> dict | None:
        """Get cached job status"""
        if not self.client:
            return None

        key = f"{self.PREFIX_STATUS}{job_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None

    def delete_job_status(self, job_id: str):
        """Delete cached job status"""
        if not self.client:
            return

        key = f"{self.PREFIX_STATUS}{job_id}"
        self.client.delete(key)

    # Job progress (for real-time updates)
    def set_job_progress(self, job_id: str, progress: int, step: str = None):
        """Update job progress in cache"""
        if not self.client:
            return

        key = f"{self.PREFIX_PROGRESS}{job_id}"
        data = {"progress": progress}
        if step:
            data["current_step"] = step

        # Short TTL for progress updates
        self.client.setex(key, 300, json.dumps(data))

    def get_job_progress(self, job_id: str) -> dict | None:
        """Get job progress from cache"""
        if not self.client:
            return None

        key = f"{self.PREFIX_PROGRESS}{job_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None

    # Result caching (compressed + base64 encoded for Redis string mode)
    def set_job_result(self, job_id: str, result: dict, ttl: int = None):
        """Cache job result (compressed and base64 encoded)"""
        if not self.client:
            return

        key = f"{self.PREFIX_RESULT}{job_id}"
        ttl = ttl or self.result_ttl

        # Compress and base64 encode for Redis string storage
        compressed = gzip.compress(json.dumps(result, default=str).encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("ascii")
        self.client.setex(key, ttl, encoded)

    def get_job_result(self, job_id: str) -> dict | None:
        """Get cached job result"""
        if not self.client:
            return None

        key = f"{self.PREFIX_RESULT}{job_id}"
        data = self.client.get(key)

        if not data:
            return None

        try:
            # Decode base64 then decompress
            compressed = base64.b64decode(data)
            decompressed = gzip.decompress(compressed)
            return json.loads(decompressed.decode("utf-8"))
        except Exception:
            # Fall back to plain JSON
            return json.loads(data)

    def delete_job_result(self, job_id: str):
        """Delete cached job result"""
        if not self.client:
            return

        key = f"{self.PREFIX_RESULT}{job_id}"
        self.client.delete(key)

    # Cleanup
    def delete_job_cache(self, job_id: str):
        """Delete all cached data for a job"""
        if not self.client:
            return

        keys = [
            f"{self.PREFIX_STATUS}{job_id}",
            f"{self.PREFIX_RESULT}{job_id}",
            f"{self.PREFIX_PROGRESS}{job_id}",
        ]
        self.client.delete(*keys)

    # Utility
    def ping(self) -> bool:
        """Check if Redis is available"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False


# Singleton instance
cache = CacheService()
