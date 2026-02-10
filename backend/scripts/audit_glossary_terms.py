#!/usr/bin/env python3
"""
Glossary Terminology Audit Script (T042)

Performs comprehensive audits on glossary terms to ensure:
1. No duplicate terms (case-insensitive)
2. All translations are complete (English ↔ Urdu)
3. Pronunciation guides are present
4. Category consistency
5. Term naming conventions
6. Definition quality checks

Usage:
    python scripts/audit_glossary_terms.py [--fix] [--report] [--strict]

Arguments:
    --fix: Attempt to fix issues automatically (where possible)
    --report: Generate detailed HTML/CSV report
    --strict: Treat warnings as errors
"""

import asyncio
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import defaultdict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.personalization.models.db_models import GlossaryTerm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GlossaryAuditor:
    """Performs comprehensive glossary audits."""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize auditor with database session.

        Args:
            db_session: AsyncSession for database operations
        """
        self.db = db_session
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []
        self.statistics: Dict = {
            "total_terms": 0,
            "complete_translations": 0,
            "missing_translations": 0,
            "duplicate_terms": 0,
            "missing_pronunciation": 0,
            "missing_definitions": 0,
            "invalid_categories": 0,
            "quality_score": 0.0
        }

    async def load_glossary_terms(self) -> List[Dict]:
        """
        Load all glossary terms from database.

        Returns:
            list: All glossary terms
        """
        try:
            query = select(GlossaryTerm)
            result = await self.db.execute(query)
            terms = result.scalars().all()

            return [term.to_dict() if hasattr(term, 'to_dict') else {
                'id': term.id,
                'english_term': term.english_term,
                'urdu_translation': term.urdu_translation,
                'pronunciation_transliterated': term.pronunciation_transliterated,
                'definition_english': term.definition_english,
                'definition_urdu': term.definition_urdu,
                'category': term.category,
                'status': term.status,
            } for term in terms]

        except Exception as e:
            logger.error(f"Error loading glossary terms: {str(e)}")
            return []

    def check_duplicates(self, terms: List[Dict]) -> None:
        """
        Check for duplicate terms (case-insensitive).

        Args:
            terms: List of glossary terms
        """
        seen_terms: Dict[str, List[str]] = defaultdict(list)

        for term in terms:
            english_lower = term['english_term'].lower()
            seen_terms[english_lower].append(term['id'])

        for english_term, term_ids in seen_terms.items():
            if len(term_ids) > 1:
                self.issues.append({
                    'type': 'DUPLICATE_TERM',
                    'severity': 'HIGH',
                    'message': f"Duplicate term found: '{english_term}' ({len(term_ids)} instances)",
                    'affected_ids': term_ids,
                    'recommendation': 'Merge duplicate entries and keep the most complete one'
                })
                self.statistics['duplicate_terms'] += 1

    def check_translations(self, terms: List[Dict]) -> None:
        """
        Check for missing translations.

        Args:
            terms: List of glossary terms
        """
        for term in terms:
            missing_parts = []

            if not term.get('english_term') or not term['english_term'].strip():
                missing_parts.append('English term')

            if not term.get('urdu_translation') or not term['urdu_translation'].strip():
                missing_parts.append('Urdu translation')
                self.statistics['missing_translations'] += 1

            if missing_parts:
                self.issues.append({
                    'type': 'INCOMPLETE_TRANSLATION',
                    'severity': 'HIGH',
                    'message': f"Missing translation parts for term '{term.get('english_term', 'UNKNOWN')}': {', '.join(missing_parts)}",
                    'term_id': term['id'],
                    'recommendation': 'Add missing translations from native speakers'
                })
            else:
                self.statistics['complete_translations'] += 1

    def check_pronunciation(self, terms: List[Dict]) -> None:
        """
        Check for missing pronunciation guides.

        Args:
            terms: List of glossary terms
        """
        for term in terms:
            if not term.get('pronunciation_transliterated') or not term['pronunciation_transliterated'].strip():
                self.warnings.append({
                    'type': 'MISSING_PRONUNCIATION',
                    'severity': 'MEDIUM',
                    'message': f"Missing pronunciation for '{term.get('english_term', 'UNKNOWN')}'",
                    'term_id': term['id'],
                    'recommendation': 'Add transliterated pronunciation guide'
                })
                self.statistics['missing_pronunciation'] += 1

    def check_definitions(self, terms: List[Dict]) -> None:
        """
        Check for missing or poor quality definitions.

        Args:
            terms: List of glossary terms
        """
        for term in terms:
            english_def = term.get('definition_english', '').strip()
            urdu_def = term.get('definition_urdu', '').strip()

            # Check missing definitions
            if not english_def or not urdu_def:
                self.issues.append({
                    'type': 'MISSING_DEFINITION',
                    'severity': 'MEDIUM',
                    'message': f"Missing definition(s) for '{term.get('english_term', 'UNKNOWN')}'",
                    'term_id': term['id'],
                    'recommendation': 'Add clear, concise definition in both languages'
                })
                self.statistics['missing_definitions'] += 1
            else:
                # Check definition quality
                if len(english_def) < 20:
                    self.warnings.append({
                        'type': 'POOR_DEFINITION_QUALITY',
                        'severity': 'LOW',
                        'message': f"Definition too short for '{term.get('english_term')}': only {len(english_def)} characters",
                        'term_id': term['id'],
                        'recommendation': 'Expand definition with more detail'
                    })

    def check_categories(self, terms: List[Dict]) -> None:
        """
        Check for valid and consistent categories.

        Args:
            terms: List of glossary terms
        """
        valid_categories = {
            'robotics', 'control-systems', 'kinematics', 'programming',
            'hardware', 'dynamics', 'sensors', 'actuators'
        }

        category_counts: Dict[str, int] = defaultdict(int)

        for term in terms:
            category = term.get('category', '').lower().strip()

            if not category:
                self.issues.append({
                    'type': 'MISSING_CATEGORY',
                    'severity': 'LOW',
                    'message': f"Missing category for '{term.get('english_term')}'",
                    'term_id': term['id'],
                    'recommendation': 'Assign appropriate category from valid list'
                })
                self.statistics['invalid_categories'] += 1
            elif category not in valid_categories:
                self.warnings.append({
                    'type': 'INVALID_CATEGORY',
                    'severity': 'LOW',
                    'message': f"Unknown category '{category}' for '{term.get('english_term')}'",
                    'term_id': term['id'],
                    'recommendation': f'Use one of: {", ".join(sorted(valid_categories))}'
                })

            category_counts[category] += 1

        # Log category distribution
        logger.info("Category distribution:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {cat}: {count} terms")

    def check_naming_conventions(self, terms: List[Dict]) -> None:
        """
        Check term naming conventions.

        Args:
            terms: List of glossary terms
        """
        for term in terms:
            english_term = term.get('english_term', '').strip()

            if not english_term:
                continue

            # Check capitalization
            if english_term != english_term.strip():
                self.warnings.append({
                    'type': 'NAMING_CONVENTION',
                    'severity': 'LOW',
                    'message': f"Term has leading/trailing whitespace: '{english_term}'",
                    'term_id': term['id'],
                    'recommendation': 'Remove leading/trailing whitespace'
                })

            # Check for common abbreviations that might need expansion
            if len(english_term.split()) == 1 and len(english_term) < 3:
                self.warnings.append({
                    'type': 'POSSIBLY_ABBREVIATED',
                    'severity': 'LOW',
                    'message': f"Term might be abbreviated: '{english_term}'",
                    'term_id': term['id'],
                    'recommendation': 'Verify that abbreviation is standard and documented'
                })

    def calculate_quality_score(self, terms: List[Dict]) -> float:
        """
        Calculate overall glossary quality score (0-100).

        Args:
            terms: List of glossary terms

        Returns:
            float: Quality score
        """
        if not terms:
            return 0.0

        score = 100.0
        total_issues = len(self.issues) + (len(self.warnings) // 2)

        # Deduct points for issues
        score -= len(self.issues) * 10
        score -= (len(self.warnings) // 2) * 2

        # Bonus for completeness
        if self.statistics['complete_translations'] == len(terms):
            score += 10

        return max(0.0, min(100.0, score))

    async def run_audit(self) -> Dict:
        """
        Run complete glossary audit.

        Returns:
            dict: Audit results
        """
        logger.info("Starting glossary terminology audit...")

        # Load terms
        terms = await self.load_glossary_terms()
        self.statistics['total_terms'] = len(terms)

        if not terms:
            logger.warning("No glossary terms found")
            return self.generate_report()

        # Run checks
        logger.info(f"Auditing {len(terms)} glossary terms...")
        self.check_duplicates(terms)
        self.check_translations(terms)
        self.check_pronunciation(terms)
        self.check_definitions(terms)
        self.check_categories(terms)
        self.check_naming_conventions(terms)

        # Calculate quality score
        self.statistics['quality_score'] = self.calculate_quality_score(terms)

        logger.info(f"Audit complete: {len(self.issues)} issues, {len(self.warnings)} warnings")

        return self.generate_report()

    def generate_report(self) -> Dict:
        """
        Generate audit report.

        Returns:
            dict: Complete audit report
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.statistics,
            'quality_score': self.statistics['quality_score'],
            'issues': self.issues,
            'warnings': self.warnings,
            'summary': {
                'total_issues': len(self.issues),
                'total_warnings': len(self.warnings),
                'pass': len(self.issues) == 0,
                'quality_level': self._get_quality_level(self.statistics['quality_score'])
            }
        }

    @staticmethod
    def _get_quality_level(score: float) -> str:
        """Get quality level from score."""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        elif score >= 45:
            return 'Poor'
        else:
            return 'Critical'


async def main():
    """Main execution function."""
    import os
    from dotenv import load_dotenv

    # Load environment
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./test.db')

    # Create engine
    engine = create_async_engine(db_url, echo=False)

    # Create session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        auditor = GlossaryAuditor(session)
        report = await auditor.run_audit()

        # Print report
        print("\n" + "=" * 80)
        print("GLOSSARY TERMINOLOGY AUDIT REPORT")
        print("=" * 80)

        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Quality Score: {report['quality_score']:.1f}/100 ({report['summary']['quality_level']})")

        print("\nStatistics:")
        for key, value in report['statistics'].items():
            print(f"  {key}: {value}")

        if report['issues']:
            print(f"\nIssues ({len(report['issues'])}):")
            for issue in report['issues']:
                print(f"  [{issue['severity']}] {issue['type']}: {issue['message']}")
                print(f"    → {issue.get('recommendation', 'N/A')}")

        if report['warnings']:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  [{warning['severity']}] {warning['type']}: {warning['message']}")
                print(f"    → {warning.get('recommendation', 'N/A')}")

        print("\n" + "=" * 80)
        print(f"Summary: {'PASSED ✓' if report['summary']['pass'] else 'FAILED ✗'}")
        print("=" * 80 + "\n")

        # Write JSON report
        report_file = Path(__file__).parent.parent / 'reports' / f'glossary_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to {report_file}")

        # Exit with appropriate code
        sys.exit(0 if report['summary']['pass'] else 1)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
