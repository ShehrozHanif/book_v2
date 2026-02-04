-- PostgreSQL schema for User Personalization & Adaptive Learning
-- Feature: 003-personalization

-- Users table: Core user profiles with authentication
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    skill_level INTEGER DEFAULT 50 CHECK (skill_level >= 0 AND skill_level <= 100),
    skill_confidence INTEGER DEFAULT 50 CHECK (skill_confidence >= 0 AND skill_confidence <= 100),
    profile_picture_url TEXT,
    bio TEXT,
    preferences_json JSONB DEFAULT '{"explanation_style": "example_first", "code_language": "python", "learning_pace": "medium", "content_focus": "balanced"}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT username_length CHECK (char_length(username) >= 3 AND char_length(username) <= 50),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Knowledge assessments: User skill evaluations
CREATE TABLE IF NOT EXISTS knowledge_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    questions_json JSONB NOT NULL,
    calculated_skill_score INTEGER NOT NULL CHECK (calculated_skill_score >= 0 AND calculated_skill_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Learning paths: User-specific learning journey configurations
CREATE TABLE IF NOT EXISTS learning_paths (
    path_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    path_name VARCHAR(100) NOT NULL,
    chapters_array INTEGER[] NOT NULL,
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_active_path_per_user UNIQUE (user_id, status) DEFERRABLE INITIALLY DEFERRED
);

-- Progress tracking: Per-chapter learning progress
CREATE TABLE IF NOT EXISTS progress (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    chapter_id INTEGER NOT NULL CHECK (chapter_id >= 1 AND chapter_id <= 22),
    completion_status VARCHAR(20) DEFAULT 'not_started' CHECK (completion_status IN ('not_started', 'in_progress', 'completed')),
    time_spent_seconds INTEGER DEFAULT 0 CHECK (time_spent_seconds >= 0),
    mastery_score INTEGER DEFAULT 0 CHECK (mastery_score >= 0 AND mastery_score <= 100),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    practice_attempts INTEGER DEFAULT 0 CHECK (practice_attempts >= 0),
    highest_practice_score INTEGER DEFAULT 0 CHECK (highest_practice_score >= 0 AND highest_practice_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_chapter UNIQUE (user_id, chapter_id)
);

-- Achievements: Gamification badges and milestones
CREATE TABLE IF NOT EXISTS achievements (
    achievement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL,
    earned_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    display_info_json JSONB NOT NULL,
    CONSTRAINT unique_achievement_per_user UNIQUE (user_id, achievement_type)
);

-- Conversations extension: Link conversations to users (extends Spec 001)
-- This table extends the existing conversations table from Spec 001
ALTER TABLE IF EXISTS conversations
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    ADD COLUMN IF NOT EXISTS associated_chapter INTEGER CHECK (associated_chapter >= 1 AND associated_chapter <= 22);

-- Practice attempts: Track user practice sessions
CREATE TABLE IF NOT EXISTS practice_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    chapter_id INTEGER NOT NULL CHECK (chapter_id >= 1 AND chapter_id <= 22),
    questions_json JSONB NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_knowledge_assessments_user_id ON knowledge_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_assessments_created_at ON knowledge_assessments(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_status ON learning_paths(status);

CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_chapter_id ON progress(chapter_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_chapter ON progress(user_id, chapter_id);
CREATE INDEX IF NOT EXISTS idx_progress_completion_status ON progress(completion_status);

CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_achievements_earned_date ON achievements(earned_date DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_conversations_difficulty ON conversations(difficulty_level);

CREATE INDEX IF NOT EXISTS idx_practice_attempts_user_id ON practice_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_attempts_chapter_id ON practice_attempts(chapter_id);

-- Comments for documentation
COMMENT ON TABLE users IS 'User profiles with authentication and preferences';
COMMENT ON TABLE knowledge_assessments IS 'Skill assessments to establish baseline knowledge';
COMMENT ON TABLE learning_paths IS 'Personalized learning journey configurations';
COMMENT ON TABLE progress IS 'Chapter-level progress tracking with mastery scores';
COMMENT ON TABLE achievements IS 'Gamification badges and milestone rewards';
COMMENT ON TABLE practice_attempts IS 'User practice session records';

COMMENT ON COLUMN users.skill_level IS 'User skill level (0-100): 0-30=beginner, 31-70=intermediate, 71-100=advanced';
COMMENT ON COLUMN users.skill_confidence IS 'Confidence in skill assessment (0-100): affects difficulty adjustment sensitivity';
COMMENT ON COLUMN users.preferences_json IS 'User learning preferences: explanation_style, code_language, learning_pace, content_focus';
COMMENT ON COLUMN learning_paths.chapters_array IS 'Ordered array of chapter IDs in the learning path';
COMMENT ON COLUMN progress.time_spent_seconds IS 'Total time spent on this chapter in seconds';
COMMENT ON COLUMN achievements.display_info_json IS 'Badge metadata: title, description, icon_url, points';
