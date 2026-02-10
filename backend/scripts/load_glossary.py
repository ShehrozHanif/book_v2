"""
Script to load glossary terms from JSON into the database.

Usage:
    python -m src.scripts.load_glossary --env production
"""

import asyncio
import json
import logging
from pathlib import Path
from argparse import ArgumentParser
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import AsyncSession

from src.personalization.models.db_models import Base, GlossaryTerm
from src.config import DATABASE_URL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def load_glossary_terms(db: AsyncSession, json_file: Path):
    """Load glossary terms from JSON file into database."""
    
    if not json_file.exists():
        logger.error(f"Glossary JSON file not found: {json_file}")
        return 0
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        terms = data.get('glossary_terms', [])
        count = 0
        
        for term_data in terms:
            # Check if term already exists
            existing = await db.query(GlossaryTerm).filter(
                GlossaryTerm.english_term == term_data['english_term']
            ).first()
            
            if existing:
                logger.info(f"Term '{term_data['english_term']}' already exists, skipping")
                continue
            
            # Create new term
            term = GlossaryTerm(
                english_term=term_data['english_term'],
                urdu_translation=term_data['urdu_translation'],
                pronunciation_transliterated=term_data.get('pronunciation_transliterated', ''),
                definition_english=term_data['definition_english'],
                definition_urdu=term_data['definition_urdu'],
                category=term_data.get('category', 'general'),
                status='published'
            )
            db.add(term)
            count += 1
            
            if count % 10 == 0:
                await db.commit()
                logger.info(f"Loaded {count} terms...")
        
        await db.commit()
        logger.info(f"Successfully loaded {count} glossary terms")
        return count
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in glossary file: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error loading glossary terms: {e}")
        await db.rollback()
        return 0


async def main():
    """Main function to load glossary data."""
    parser = ArgumentParser(description='Load glossary terms into database')
    parser.add_argument('--env', default='development', help='Environment (development/production)')
    args = parser.parse_args()
    
    # Determine database URL based on environment
    db_url = DATABASE_URL
    
    # Create engine and session
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Load glossary terms
    glossary_file = Path(__file__).parent.parent / 'src' / 'personalization' / 'data' / 'glossary_terms.json'
    
    async with async_session() as session:
        count = await load_glossary_terms(session, glossary_file)
        logger.info(f"Load operation completed. Loaded {count} terms.")
    
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
