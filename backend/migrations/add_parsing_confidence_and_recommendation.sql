-- Migration: Add parsing confidence and AI recommendation fields
-- Run this migration to update the database schema

-- Add parsing_confidence to candidates table
ALTER TABLE candidates 
ADD COLUMN IF NOT EXISTS parsing_confidence FLOAT DEFAULT 0;

-- Add AI recommendation fields
ALTER TABLE candidates 
ADD COLUMN IF NOT EXISTS ai_recommendation VARCHAR(50);

ALTER TABLE candidates 
ADD COLUMN IF NOT EXISTS ai_recommendation_reasoning TEXT;

-- Update work_experience to ensure duration_months has default
ALTER TABLE work_experience 
ALTER COLUMN duration_months SET DEFAULT 0;

-- Add comment for documentation
COMMENT ON COLUMN candidates.parsing_confidence IS 'Confidence score (0-1) for resume parsing quality';
COMMENT ON COLUMN candidates.ai_recommendation IS 'AI hiring recommendation: strong_yes, yes, maybe, no';
COMMENT ON COLUMN candidates.ai_recommendation_reasoning IS 'AI explanation for the recommendation';
