"""Add chatbot translation tables for Urdu translation feature.

Revision ID: 003
Revises: 002_add_indexes
Create Date: 2026-02-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create 6 new tables for chatbot translation feature."""

    # Create ChatbotResponseTemplate table
    op.create_table(
        'chatbot_response_template',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('template_key', sa.String(255), nullable=False, unique=True),
        sa.Column('english_content', sa.Text, nullable=False),
        sa.Column('version', sa.Integer, nullable=False, default=1),
        sa.Column('status', sa.String(50), nullable=False, default='published'),  # published, draft, archived
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_key', name='uq_chatbot_template_key'),
        sa.Index('idx_chatbot_template_status', 'status'),
        sa.Index('idx_chatbot_template_key', 'template_key'),
    )

    # Create ChatbotTranslation table
    op.create_table(
        'chatbot_translation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('response_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('language', sa.String(50), nullable=False),  # urdu, etc.
        sa.Column('translated_content', sa.Text, nullable=True),  # nullable until translated
        sa.Column('translator_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer, nullable=False, default=1),  # tracks English version this translation covers
        sa.Column('status', sa.String(50), nullable=False, default='draft'),  # draft, in_review, published
        sa.Column('translated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['response_template_id'], ['chatbot_response_template.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['translator_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('response_template_id', 'language', name='uq_translation_template_language'),
        sa.Index('idx_translation_template_status', 'response_template_id', 'status'),
        sa.Index('idx_translation_language_status', 'language', 'status'),
    )

    # Create GlossaryTerm table
    op.create_table(
        'glossary_term',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('english_term', sa.String(255), nullable=False, unique=True),
        sa.Column('urdu_translation', sa.String(255), nullable=False),
        sa.Column('pronunciation_transliterated', sa.String(255), nullable=False),  # Latin characters
        sa.Column('definition_english', sa.Text, nullable=False),
        sa.Column('definition_urdu', sa.Text, nullable=False),
        sa.Column('category', sa.String(100), nullable=True),  # robotics, control, kinematics, etc.
        sa.Column('status', sa.String(50), nullable=False, default='published'),  # published, under_review
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('english_term', name='uq_glossary_english_term'),
        sa.Index('idx_glossary_term', 'english_term'),
        sa.Index('idx_glossary_category', 'category'),
    )

    # Create GlossaryFeedback table
    op.create_table(
        'glossary_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('glossary_term_id', postgresql.UUID(as_uuid=True), nullable=True),  # nullable for new term suggestions
        sa.Column('suggested_term', sa.String(255), nullable=True),  # for new term suggestions
        sa.Column('feedback_type', sa.String(50), nullable=False),  # suggestion, correction, new_term
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),  # pending, accepted, rejected
        sa.Column('admin_response', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['glossary_term_id'], ['glossary_term.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_feedback_user', 'user_id'),
        sa.Index('idx_feedback_term', 'glossary_term_id'),
        sa.Index('idx_feedback_status', 'status'),
    )

    # Create UserLanguagePreference table
    op.create_table(
        'user_language_preference',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('language', sa.String(50), nullable=False, default='english'),  # english, urdu
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_language_preference'),
        sa.Index('idx_user_language', 'user_id'),
    )

    # Create ChatbotResponseTranslationStatus table
    op.create_table(
        'chatbot_response_translation_status',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('response_template_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('english_version', sa.Integer, nullable=False, default=1),
        sa.Column('urdu_version', sa.Integer, nullable=True),  # nullable until translated
        sa.Column('status', sa.String(50), nullable=False, default='needs_translation'),  # translated, needs_translation, needs_review, stale
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['response_template_id'], ['chatbot_response_template.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('response_template_id', name='uq_translation_status_template'),
        sa.Index('idx_translation_status', 'status'),
        sa.Index('idx_translation_status_language', 'status'),
    )


def downgrade() -> None:
    """Drop all 6 tables created for chatbot translation feature."""
    op.drop_table('chatbot_response_translation_status')
    op.drop_table('user_language_preference')
    op.drop_table('glossary_feedback')
    op.drop_table('glossary_term')
    op.drop_table('chatbot_translation')
    op.drop_table('chatbot_response_template')
