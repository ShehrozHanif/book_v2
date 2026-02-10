"""Add personalization tables

Revision ID: 001
Revises:
Create Date: 2026-02-07 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create personalization tables."""

    # Users table: Core user profiles with authentication
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('skill_level', sa.Integer, nullable=False, server_default='50'),
        sa.Column('skill_confidence', sa.Integer, nullable=False, server_default='50'),
        sa.Column('is_admin', sa.Integer, nullable=False, server_default='0'),
        sa.Column('profile_picture_url', sa.Text, nullable=True),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('preferences_json', postgresql.JSONB, nullable=False, server_default=sa.text(
            "'{\"explanation_style\": \"example_first\", \"code_language\": \"python\", \"learning_pace\": \"medium\", \"content_focus\": \"balanced\"}'"
        )),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint('skill_level >= 0 AND skill_level <= 100', name='check_skill_level_range'),
        sa.CheckConstraint('skill_confidence >= 0 AND skill_confidence <= 100', name='check_skill_confidence_range'),
        sa.CheckConstraint('char_length(username) >= 3 AND char_length(username) <= 50', name='username_length'),
        sa.CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'", name='email_format'),
    )

    # Indexes for users table
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_deleted_at', 'users', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))

    # Knowledge assessments: User skill evaluations
    op.create_table(
        'knowledge_assessments',
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('questions_json', postgresql.JSONB, nullable=False),
        sa.Column('calculated_skill_score', sa.Integer, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.CheckConstraint('calculated_skill_score >= 0 AND calculated_skill_score <= 100', name='check_assessment_score_range'),
    )

    # Indexes for knowledge_assessments table
    op.create_index('idx_knowledge_assessments_user_id', 'knowledge_assessments', ['user_id'])
    op.create_index('idx_knowledge_assessments_created_at', 'knowledge_assessments', ['created_at'], postgresql_using='btree')

    # Learning paths: User-specific learning journey configurations
    op.create_table(
        'learning_paths',
        sa.Column('path_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('path_name', sa.String(100), nullable=False),
        sa.Column('chapters_array', postgresql.ARRAY(sa.Integer), nullable=False),
        sa.Column('completion_percentage', sa.Integer, nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100', name='check_completion_range'),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned')", name='check_status_values'),
    )

    # Indexes for learning_paths table
    op.create_index('idx_learning_paths_user_id', 'learning_paths', ['user_id'])
    op.create_index('idx_learning_paths_status', 'learning_paths', ['status'])

    # Progress tracking: Per-chapter learning progress
    op.create_table(
        'progress',
        sa.Column('progress_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', sa.Integer, nullable=False),
        sa.Column('completion_status', sa.String(20), nullable=False, server_default='not_started'),
        sa.Column('time_spent_seconds', sa.Integer, nullable=False, server_default='0'),
        sa.Column('mastery_score', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('practice_attempts', sa.Integer, nullable=False, server_default='0'),
        sa.Column('highest_practice_score', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.CheckConstraint('chapter_id >= 1 AND chapter_id <= 22', name='check_chapter_id_range'),
        sa.CheckConstraint("completion_status IN ('not_started', 'in_progress', 'completed')", name='check_completion_status_values'),
        sa.CheckConstraint('time_spent_seconds >= 0', name='check_time_spent_positive'),
        sa.CheckConstraint('mastery_score >= 0 AND mastery_score <= 100', name='check_mastery_score_range'),
        sa.CheckConstraint('practice_attempts >= 0', name='check_practice_attempts_positive'),
        sa.CheckConstraint('highest_practice_score >= 0 AND highest_practice_score <= 100', name='check_highest_practice_score_range'),
        sa.UniqueConstraint('user_id', 'chapter_id', name='unique_user_chapter'),
    )

    # Indexes for progress table
    op.create_index('idx_progress_user_id', 'progress', ['user_id'])
    op.create_index('idx_progress_chapter_id', 'progress', ['chapter_id'])
    op.create_index('idx_progress_user_chapter', 'progress', ['user_id', 'chapter_id'])
    op.create_index('idx_progress_completion_status', 'progress', ['completion_status'])

    # Achievements: Gamification badges and milestones
    op.create_table(
        'achievements',
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_type', sa.String(100), nullable=False),
        sa.Column('earned_date', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('display_info_json', postgresql.JSONB, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'achievement_type', name='unique_achievement_per_user'),
    )

    # Indexes for achievements table
    op.create_index('idx_achievements_user_id', 'achievements', ['user_id'])
    op.create_index('idx_achievements_earned_date', 'achievements', ['earned_date'], postgresql_using='btree')

    # Practice attempts: Track user practice sessions
    op.create_table(
        'practice_attempts',
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', sa.Integer, nullable=False),
        sa.Column('questions_json', postgresql.JSONB, nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('attempted_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.CheckConstraint('chapter_id >= 1 AND chapter_id <= 22', name='check_practice_chapter_id_range'),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_practice_score_range'),
    )

    # Indexes for practice_attempts table
    op.create_index('idx_practice_attempts_user_id', 'practice_attempts', ['user_id'])
    op.create_index('idx_practice_attempts_chapter_id', 'practice_attempts', ['chapter_id'])

    # Add comments for documentation
    op.execute("COMMENT ON TABLE users IS 'User profiles with authentication and preferences'")
    op.execute("COMMENT ON TABLE knowledge_assessments IS 'Skill assessments to establish baseline knowledge'")
    op.execute("COMMENT ON TABLE learning_paths IS 'Personalized learning journey configurations'")
    op.execute("COMMENT ON TABLE progress IS 'Chapter-level progress tracking with mastery scores'")
    op.execute("COMMENT ON TABLE achievements IS 'Gamification badges and milestone rewards'")
    op.execute("COMMENT ON TABLE practice_attempts IS 'User practice session records'")

    op.execute("COMMENT ON COLUMN users.skill_level IS 'User skill level (0-100): 0-30=beginner, 31-70=intermediate, 71-100=advanced'")
    op.execute("COMMENT ON COLUMN users.skill_confidence IS 'Confidence in skill assessment (0-100): affects difficulty adjustment sensitivity'")
    op.execute("COMMENT ON COLUMN users.preferences_json IS 'User learning preferences: explanation_style, code_language, learning_pace, content_focus'")
    op.execute("COMMENT ON COLUMN learning_paths.chapters_array IS 'Ordered array of chapter IDs in the learning path'")
    op.execute("COMMENT ON COLUMN progress.time_spent_seconds IS 'Total time spent on this chapter in seconds'")
    op.execute("COMMENT ON COLUMN achievements.display_info_json IS 'Badge metadata: title, description, icon_url, points'")


def downgrade() -> None:
    """Drop personalization tables."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('practice_attempts')
    op.drop_table('achievements')
    op.drop_table('progress')
    op.drop_table('learning_paths')
    op.drop_table('knowledge_assessments')
    op.drop_table('users')
