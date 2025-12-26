-- WhatsApp Wrapped Backend Schema
-- Run this directly in Neon SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_step VARCHAR(100),

    -- File info
    original_filename VARCHAR(255),
    file_key VARCHAR(255),
    file_size INTEGER,

    -- Processing params
    year_filter INTEGER CHECK (year_filter >= 2009 AND year_filter <= 2030),

    -- Results
    result_key VARCHAR(255),
    message_count INTEGER,
    participant_count INTEGER,
    group_name VARCHAR(255),

    -- Error handling
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Client info (for rate limiting/analytics)
    client_ip VARCHAR(45),
    user_agent TEXT
);

-- Indexes for common queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_expires_at ON jobs(expires_at)
    WHERE expires_at IS NOT NULL;

-- Function to auto-set expires_at on insert
CREATE OR REPLACE FUNCTION set_job_expiry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.expires_at := NOW() + INTERVAL '2 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-expiry
DROP TRIGGER IF EXISTS trigger_set_job_expiry ON jobs;
CREATE TRIGGER trigger_set_job_expiry
    BEFORE INSERT ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION set_job_expiry();

-- View for monitoring
CREATE OR REPLACE VIEW job_stats AS
SELECT
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at)))::INTEGER as avg_duration_seconds
FROM jobs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status;

-- Cleanup function (call periodically or via pg_cron)
CREATE OR REPLACE FUNCTION cleanup_expired_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM jobs WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
