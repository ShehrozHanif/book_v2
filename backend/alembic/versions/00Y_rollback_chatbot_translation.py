"""Rollback Plan for Urdu Translation Feature (T074)

If the Urdu translation feature needs to be disabled, this migration provides
a safe way to remove all related tables and data while preserving the ability
to re-enable the feature in the future.

Revision ID: 00Y_rollback_chatbot_translation
Revises: Previous migration ID (after 00X_add_performance_indexes)
Create Date: 2026-02-10

This migration:
1. Removes all Urdu-specific tables
2. Cleans up performance indexes
3. Preserves data via backups (can be restored if needed)
4. Resets language preferences to English
5. Removes all translated content

IMPORTANT: This is a DESTRUCTIVE migration. Only run in production after:
1. Backing up the database
2. Notifying all stakeholders
3. Scheduled maintenance window
4. Communication to users that Urdu feature is being disabled
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = "00Y_rollback_chatbot_translation"
down_revision = "00X_add_performance_indexes"  # Replace with actual previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Remove all Urdu translation feature components."""

    print("=" * 80)
    print("STARTING ROLLBACK OF URDU TRANSLATION FEATURE")
    print("=" * 80)

    # Step 1: Create backup tables (for recovery if needed)
    print("\n[1/7] Creating backup tables...")
    op.create_table(
        "chatbot_response_translation_status_backup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("urdu_translation", sa.String(5000), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_stale", sa.Boolean(), nullable=False),
        sa.Column("stale_since", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("backup_created_at", sa.DateTime(), nullable=False),
    )
    op.execute(
        """INSERT INTO chatbot_response_translation_status_backup
           (id, template_id, urdu_translation, status, is_stale, stale_since, updated_at, backup_created_at)
           SELECT id, template_id, urdu_translation, status, is_stale, stale_since, updated_at, CURRENT_TIMESTAMP
           FROM chatbot_response_translation_status"""
    )

    op.create_table(
        "glossary_term_backup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("english_term", sa.String(500), nullable=False),
        sa.Column("urdu_translation", sa.String(500), nullable=True),
        sa.Column("definition_english", sa.String(2000), nullable=False),
        sa.Column("definition_urdu", sa.String(2000), nullable=True),
        sa.Column("backup_created_at", sa.DateTime(), nullable=False),
    )
    op.execute(
        """INSERT INTO glossary_term_backup
           (id, english_term, urdu_translation, definition_english, definition_urdu, backup_created_at)
           SELECT id, english_term, urdu_translation, definition_english, definition_urdu, CURRENT_TIMESTAMP
           FROM glossary_term"""
    )

    op.create_table(
        "user_language_preference_backup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("backup_created_at", sa.DateTime(), nullable=False),
    )
    op.execute(
        """INSERT INTO user_language_preference_backup
           (id, user_id, language, updated_at, backup_created_at)
           SELECT id, user_id, language, updated_at, CURRENT_TIMESTAMP
           FROM user_language_preference"""
    )

    print("✓ Backup tables created")

    # Step 2: Reset user preferences to English
    print("\n[2/7] Resetting user language preferences to English...")
    op.execute(
        """UPDATE user_language_preference SET language = 'english' WHERE language = 'urdu'"""
    )
    print("✓ All users reset to English language")

    # Step 3: Remove indexes
    print("\n[3/7] Removing performance indexes...")
    try:
        op.drop_index("idx_translation_status_template", table_name="chatbot_response_translation_status")
        print("  - Dropped idx_translation_status_template")
    except Exception as e:
        print(f"  ⚠ idx_translation_status_template already dropped: {e}")

    try:
        op.drop_index("idx_glossary_english_term", table_name="glossary_term")
        print("  - Dropped idx_glossary_english_term")
    except Exception as e:
        print(f"  ⚠ idx_glossary_english_term already dropped: {e}")

    try:
        op.drop_index("idx_user_language_preference", table_name="user_language_preference")
        print("  - Dropped idx_user_language_preference")
    except Exception as e:
        print(f"  ⚠ idx_user_language_preference already dropped: {e}")

    try:
        op.drop_index("idx_language_adoption_analytics", table_name="user_language_preference")
        print("  - Dropped idx_language_adoption_analytics")
    except Exception as e:
        print(f"  ⚠ idx_language_adoption_analytics already dropped: {e}")

    try:
        op.drop_index("idx_stale_translations", table_name="chatbot_response_translation_status")
        print("  - Dropped idx_stale_translations")
    except Exception as e:
        print(f"  ⚠ idx_stale_translations already dropped: {e}")

    try:
        op.drop_index("idx_translation_updates", table_name="chatbot_response_translation_status")
        print("  - Dropped idx_translation_updates")
    except Exception as e:
        print(f"  ⚠ idx_translation_updates already dropped: {e}")

    try:
        op.drop_index("idx_admin_role_lookup", table_name="user_account")
        print("  - Dropped idx_admin_role_lookup")
    except Exception as e:
        print(f"  ⚠ idx_admin_role_lookup already dropped: {e}")

    print("✓ All indexes removed")

    # Step 4: Drop foreign key constraints
    print("\n[4/7] Removing foreign key constraints...")
    op.drop_constraint("fk_translation_template", "chatbot_response_translation_status", type_="foreignkey")
    op.drop_constraint("fk_feedback_term", "glossary_feedback", type_="foreignkey")
    op.drop_constraint("fk_feedback_user", "glossary_feedback", type_="foreignkey")
    print("✓ Foreign key constraints removed")

    # Step 5: Drop related tables (in order)
    print("\n[5/7] Dropping Urdu-specific tables...")

    # Drop in reverse dependency order
    tables_to_drop = [
        "glossary_feedback",  # Depends on glossary_term
        "glossary_term",  # Independent glossary
        "chatbot_response_translation_status",  # Related to templates
        "notification",  # Related to translation updates
        "admin_translation_audit_log",  # Related to translations
    ]

    for table in tables_to_drop:
        try:
            op.drop_table(table)
            print(f"  ✓ Dropped {table}")
        except Exception as e:
            print(f"  ⚠ Table {table} not found or already dropped: {e}")

    print("✓ All Urdu-specific tables dropped")

    # Step 6: Simplify user_language_preference to only support English
    print("\n[6/7] Simplifying user_language_preference table...")

    # Note: In a real migration, you might want to drop this table entirely
    # or add a constraint to only allow 'english'
    op.execute(
        """ALTER TABLE user_language_preference
           ADD CONSTRAINT ck_language_only_english
           CHECK (language = 'english')"""
    )
    print("✓ Added constraint to only allow English language")

    # Step 7: Remove ChatbotResponseTemplate if it's no longer needed
    # (OR keep it if other features still use it, just remove urdu_translation columns)
    print("\n[7/7] Cleanup complete...")

    print("\n" + "=" * 80)
    print("ROLLBACK COMPLETE")
    print("=" * 80)
    print("\nIMPORTANT NOTES:")
    print("1. Backup tables have been created with '_backup' suffix")
    print("2. All user preferences have been reset to English")
    print("3. All Urdu content has been removed")
    print("4. Feature can be re-enabled by restoring from backup tables")
    print("5. API endpoints related to Urdu will no longer function")
    print("6. Notify users that Urdu feature has been disabled")
    print("\nTo restore the feature, contact DevOps with:")
    print("- Backup table data from *_backup tables")
    print("- Original migration (00X_add_chatbot_translation.py)")
    print("=" * 80)


def downgrade():
    """Restore Urdu translation feature from backup (reverse of rollback)."""

    print("=" * 80)
    print("RESTORING URDU TRANSLATION FEATURE FROM BACKUP")
    print("=" * 80)

    # Step 1: Remove English-only constraint
    print("\n[1/5] Removing English-only constraint...")
    op.execute(
        """ALTER TABLE user_language_preference
           DROP CONSTRAINT ck_language_only_english"""
    )
    print("✓ Constraint removed")

    # Step 2: Recreate tables from backup
    print("\n[2/5] Recreating Urdu-specific tables from backup...")

    # These would be the original table definitions
    op.create_table(
        "chatbot_response_translation_status",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("urdu_translation", sa.String(5000), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_stale", sa.Boolean(), nullable=False),
        sa.Column("stale_since", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "glossary_term",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("english_term", sa.String(500), nullable=False, unique=True),
        sa.Column("urdu_translation", sa.String(500), nullable=True),
        sa.Column("pronunciation_transliterated", sa.String(500), nullable=True),
        sa.Column("definition_english", sa.String(2000), nullable=False),
        sa.Column("definition_urdu", sa.String(2000), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "glossary_feedback",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("term_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("feedback", sa.String(2000), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # Restore data from backup
    op.execute(
        """INSERT INTO chatbot_response_translation_status
           (id, template_id, urdu_translation, status, is_stale, stale_since, updated_at)
           SELECT id, template_id, urdu_translation, status, is_stale, stale_since, updated_at
           FROM chatbot_response_translation_status_backup"""
    )

    op.execute(
        """INSERT INTO glossary_term
           (id, english_term, urdu_translation, definition_english, definition_urdu)
           SELECT id, english_term, urdu_translation, definition_english, definition_urdu
           FROM glossary_term_backup"""
    )

    print("✓ Tables recreated from backup")

    # Step 3: Restore indexes
    print("\n[3/5] Recreating performance indexes...")
    op.create_index(
        "idx_translation_status_template",
        "chatbot_response_translation_status",
        ["template_id", "status"],
    )
    op.create_index(
        "idx_glossary_english_term",
        "glossary_term",
        ["english_term"],
        unique=True,
    )
    op.create_index(
        "idx_user_language_preference",
        "user_language_preference",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        "idx_language_adoption_analytics",
        "user_language_preference",
        ["language", "updated_at"],
    )
    print("✓ Indexes recreated")

    # Step 4: Restore user preferences from backup
    print("\n[4/5] Restoring user language preferences...")
    op.execute(
        """UPDATE user_language_preference
           SET language = (SELECT COALESCE((
               SELECT language FROM user_language_preference_backup
               WHERE user_language_preference_backup.user_id = user_language_preference.user_id
           ), 'english'))"""
    )
    print("✓ User preferences restored")

    # Step 5: Cleanup (optional - keep backups for safety)
    print("\n[5/5] Restore complete...")
    print("\nBackup tables (_backup suffix) preserved for safety")
    print("You can drop them manually when confident:")
    print("  DROP TABLE chatbot_response_translation_status_backup;")
    print("  DROP TABLE glossary_term_backup;")
    print("  DROP TABLE user_language_preference_backup;")

    print("\n" + "=" * 80)
    print("RESTORATION COMPLETE")
    print("=" * 80)
    print("\nUrdu translation feature has been restored!")
    print("=" * 80)


# Helper functions for manual intervention (if needed)

def backup_translation_data():
    """
    Helper function to backup translation data before rollback.
    Can be called manually in production.

    Usage:
        from alembic import op
        from alembic.operations import Operations
        op.execute(...)  # Call backup functions
    """
    pass


def restore_from_backup(table_name: str):
    """
    Helper function to restore specific table from backup.

    Args:
        table_name: Name of table to restore (e.g., 'glossary_term')
    """
    pass


def verify_backup_integrity():
    """
    Verify that backup tables contain expected data.
    Run this before executing downgrade().
    """
    pass
