-- Migration: Add conversation_id and processing_time_ms to audit_logs
-- Date: 2024-01-30
-- Description: Adds tracking for conversation context and performance metrics

BEGIN;

-- Add conversation_id column
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS conversation_id UUID REFERENCES conversations(conversation_id);

-- Add processing_time_ms column
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS processing_time_ms FLOAT8;

-- Add index for conversation_id lookups
CREATE INDEX IF NOT EXISTS idx_audit_logs_conversation_id ON audit_logs(conversation_id);

COMMIT;
