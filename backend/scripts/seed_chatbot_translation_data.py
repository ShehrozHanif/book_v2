"""
Database seeding script for chatbot translation feature.

Loads:
1. Glossary terms (150+ technical terms with bilingual definitions)
2. Response templates (50+ chatbot response templates)

Run with: python scripts/seed_chatbot_translation_data.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so src module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models
from src.personalization.models.db_models import (
    GlossaryTerm,
    ChatbotResponseTemplate,
    ChatbotResponseTranslationStatus,
)
from src.config import get_settings


class ChatbotTranslationSeeder:
    """Seeder for chatbot translation data."""

    def __init__(self):
        """Initialize seeder with database connection."""
        self.settings = get_settings()
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """Initialize database connection."""
        try:
            self.engine = create_async_engine(
                self.settings.DATABASE_URL,
                echo=False,
                future=True,
            )
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                future=True,
            )
            logger.info("✅ Database connection initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    async def cleanup(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("✅ Database connection closed")

    async def load_glossary_terms(self):
        """Load glossary terms from JSON file."""
        glossary_file = Path(__file__).parent.parent / "src/personalization/data/glossary_terms.json"

        if not glossary_file.exists():
            logger.warning(f"❌ Glossary file not found: {glossary_file}")
            return 0

        try:
            with open(glossary_file, 'r', encoding='utf-8') as f:
                terms_data = json.load(f)

            async with self.async_session() as session:
                loaded_count = 0
                skipped_count = 0

                for term_data in terms_data:
                    try:
                        # Check if term already exists
                        from sqlalchemy import select
                        existing = await session.execute(
                            select(GlossaryTerm).where(
                                GlossaryTerm.english_term == term_data['english_term']
                            )
                        )
                        if existing.scalar_one_or_none():
                            skipped_count += 1
                            continue

                        term = GlossaryTerm(
                            english_term=term_data['english_term'],
                            urdu_translation=term_data['urdu_translation'],
                            pronunciation_transliterated=term_data['pronunciation_transliterated'],
                            definition_english=term_data['definition_english'],
                            definition_urdu=term_data['definition_urdu'],
                            category=term_data.get('category'),
                            status='published',
                        )
                        session.add(term)
                        loaded_count += 1

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load term '{term_data.get('english_term')}': {e}")
                        continue

                await session.commit()
                logger.info(f"✅ Loaded {loaded_count} glossary terms ({skipped_count} already exist)")
                return loaded_count

        except Exception as e:
            logger.error(f"❌ Failed to load glossary terms: {e}")
            raise

    async def load_response_templates(self):
        """Load response templates from JSON file."""
        templates_file = Path(__file__).parent.parent / "src/personalization/data/response_templates.json"

        if not templates_file.exists():
            logger.warning(f"❌ Templates file not found: {templates_file}")
            return 0

        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)

            async with self.async_session() as session:
                loaded_count = 0
                skipped_count = 0

                for template_data in templates_data:
                    try:
                        # Check if template already exists
                        from sqlalchemy import select
                        existing = await session.execute(
                            select(ChatbotResponseTemplate).where(
                                ChatbotResponseTemplate.template_key == template_data['template_key']
                            )
                        )
                        if existing.scalar_one_or_none():
                            skipped_count += 1
                            continue

                        template = ChatbotResponseTemplate(
                            template_key=template_data['template_key'],
                            english_content=template_data['english_content'],
                            version=1,
                            status='published',
                        )
                        session.add(template)
                        await session.flush()  # Flush to get template ID

                        # Also create translation status record with template ID
                        status = ChatbotResponseTranslationStatus(
                            response_template_id=template.id,  # Now we have the ID
                            english_version=1,
                            urdu_version=None,
                            status='needs_translation',
                        )
                        session.add(status)

                        loaded_count += 1

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load template '{template_data.get('template_key')}': {e}")
                        continue

                await session.commit()
                logger.info(f"✅ Loaded {loaded_count} response templates ({skipped_count} already exist)")
                return loaded_count

        except Exception as e:
            logger.error(f"❌ Failed to load response templates: {e}")
            raise

    async def seed_all(self):
        """Seed all data."""
        logger.info("=" * 60)
        logger.info("🌱 Starting Chatbot Translation Data Seeding")
        logger.info("=" * 60)

        try:
            await self.initialize()

            # Load glossary terms
            glossary_count = await self.load_glossary_terms()

            # Load response templates
            templates_count = await self.load_response_templates()

            logger.info("=" * 60)
            logger.info(f"✅ Seeding Complete!")
            logger.info(f"   - Glossary Terms: {glossary_count}")
            logger.info(f"   - Response Templates: {templates_count}")
            logger.info(f"   - Total Records: {glossary_count + templates_count}")
            logger.info("=" * 60)

            return {
                "glossary_terms": glossary_count,
                "response_templates": templates_count,
                "total": glossary_count + templates_count,
            }

        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point."""
    seeder = ChatbotTranslationSeeder()
    await seeder.seed_all()


if __name__ == "__main__":
    asyncio.run(main())
