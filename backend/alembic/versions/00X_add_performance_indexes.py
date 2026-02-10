"""Add performance indexes for Urdu translation feature (T067)

Revision ID: 00X_add_performance_indexes
Revises: previous_migration
Create Date: 2026-02-10

Performance optimization through strategic indexing:
- Translation status lookups: (template_id, status)
- Glossary term searches: (english_term)
- User language preferences: (user_id)
- Analytics queries: (language, updated_at)
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "00X_add_performance_indexes"
down_revision = "PREVIOUS_MIGRATION_ID"
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for performance optimization."""

    # Index for translation status lookups
    op.create_index(
        "idx_translation_status_template",
        "chatbot_response_translation_status",
        ["template_id", "status"],
        postgresql_where=sa.text("status IS NOT NULL"),
    )

    # Index for glossary term searches
    op.create_index(
        "idx_glossary_english_term",
        "glossary_term",
        ["english_term"],
        unique=True,
    )

    # Index for user language preferences
    op.create_index(
        "idx_user_language_preference",
        "user_language_preference",
        ["user_id"],
        unique=True,
    )

    # Index for analytics queries
    op.create_index(
        "idx_language_adoption_analytics",
        "user_language_preference",
        ["language", "updated_at"],
    )

    # Index for stale translation detection
    op.create_index(
        "idx_stale_translations",
        "chatbot_response_translation_status",
        ["is_stale", "stale_since"],
        postgresql_where=sa.text("is_stale = true"),
    )

    # Index for admin translation updates
    op.create_index(
        "idx_translation_updates",
        "chatbot_response_translation_status",
        ["updated_at"],
        postgresql_where=sa.text("status IN ('reviewed', 'published')"),
    )

    # Index for notification queries
    op.create_index(
        "idx_admin_role_lookup",
        "user_account",
        ["role"],
        postgresql_where=sa.text("role IN ('admin', 'instructor')"),
    )

    print("Added 7 performance indexes")


def downgrade():
    """Remove indexes."""

    op.drop_index("idx_translation_status_template")
    op.drop_index("idx_glossary_english_term")
    op.drop_index("idx_user_language_preference")
    op.drop_index("idx_language_adoption_analytics")
    op.drop_index("idx_stale_translations")
    op.drop_index("idx_translation_updates")
    op.drop_index("idx_admin_role_lookup")

    print("Removed 7 performance indexes")
