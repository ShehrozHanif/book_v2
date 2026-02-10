#!/usr/bin/env python3
"""
Translation Audit Report Script (T052)

Generates comprehensive report of translation status:
- Which templates need translation/refresh
- Completion percentages
- Translator activity
- Stale translation details
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from src.personalization.models.db_models import (
    Base,
    ChatbotResponseTemplate,
    ChatbotResponseTranslationStatus,
    User
)
from src.config import get_settings


async def generate_translation_report() -> Dict[str, Any]:
    """
    Generate comprehensive translation audit report.

    Returns:
        Dictionary containing all report data
    """
    settings = get_settings()

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    try:
        async with async_session() as session:
            # Get all templates and translations
            templates_result = await session.execute(
                select(ChatbotResponseTemplate)
            )
            templates = templates_result.scalars().all()

            translations_result = await session.execute(
                select(ChatbotResponseTranslationStatus)
            )
            translations = translations_result.scalars().all()

            # Create lookup map
            trans_map = {t.template_id: t for t in translations}

            # Generate report data
            total_templates = len(templates)

            needs_translation = []
            needs_review = []
            stale_translations = []
            published_count = 0
            reviewed_count = 0
            draft_count = 0

            for template in templates:
                trans = trans_map.get(template.id)

                if not trans:
                    needs_translation.append({
                        "template_id": template.id,
                        "template_key": template.key,
                        "english_content": template.content[:100] + "..." if len(template.content) > 100 else template.content,
                    })
                else:
                    if not trans.urdu_translation:
                        needs_translation.append({
                            "template_id": template.id,
                            "template_key": template.key,
                            "english_content": template.content[:100] + "..." if len(template.content) > 100 else template.content,
                        })

                    if trans.status == "draft":
                        draft_count += 1
                        needs_review.append({
                            "template_id": template.id,
                            "template_key": template.key,
                            "status": trans.status,
                            "updated_at": trans.updated_at.isoformat() if trans.updated_at else None,
                        })
                    elif trans.status == "reviewed":
                        reviewed_count += 1
                    elif trans.status == "published":
                        published_count += 1

                    if trans.is_stale:
                        stale_translations.append({
                            "template_id": template.id,
                            "template_key": template.key,
                            "stale_since": trans.stale_since.isoformat() if trans.stale_since else None,
                            "urdu_translation": trans.urdu_translation[:50] + "..." if trans.urdu_translation and len(trans.urdu_translation) > 50 else trans.urdu_translation,
                        })

            # Calculate percentages
            translated_count = sum(1 for t in translations if t.urdu_translation)
            translation_percent = (translated_count / total_templates * 100) if total_templates > 0 else 0
            review_percent = (reviewed_count / total_templates * 100) if total_templates > 0 else 0
            published_percent = (published_count / total_templates * 100) if total_templates > 0 else 0

            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_templates": total_templates,
                    "translated": {
                        "count": translated_count,
                        "percentage": round(translation_percent, 2),
                    },
                    "reviewed": {
                        "count": reviewed_count,
                        "percentage": round(review_percent, 2),
                    },
                    "published": {
                        "count": published_count,
                        "percentage": round(published_percent, 2),
                    },
                    "draft": {
                        "count": draft_count,
                        "percentage": round((draft_count / total_templates * 100) if total_templates > 0 else 0, 2),
                    },
                    "stale": {
                        "count": len(stale_translations),
                        "percentage": round((len(stale_translations) / total_templates * 100) if total_templates > 0 else 0, 2),
                    },
                },
                "needs_translation": {
                    "count": len(needs_translation),
                    "templates": needs_translation,
                },
                "needs_review": {
                    "count": len(needs_review),
                    "templates": needs_review,
                },
                "stale_translations": {
                    "count": len(stale_translations),
                    "templates": stale_translations,
                },
                "completion_metrics": {
                    "overall_completion": round(
                        (published_count + reviewed_count) / total_templates * 100
                        if total_templates > 0 else 0,
                        2
                    ),
                    "ready_to_publish": reviewed_count,
                    "urgent_actions": len(needs_translation) + len(stale_translations),
                },
            }

            return report

    finally:
        await engine.dispose()


async def save_report_to_file(report: Dict[str, Any], filename: str = None) -> str:
    """
    Save report to JSON file.

    Args:
        report: Report data dictionary
        filename: Output filename (default: translation_report_TIMESTAMP.json)

    Returns:
        Path to saved file
    """
    if not filename:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"translation_report_{timestamp}.json"

    output_path = Path(__file__).parent.parent / "reports" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(output_path)


def print_report_summary(report: Dict[str, Any]) -> None:
    """Print human-readable summary of report."""
    print("\n" + "="*80)
    print("TRANSLATION AUDIT REPORT")
    print("="*80)
    print(f"\nGenerated: {report['generated_at']}\n")

    summary = report["summary"]
    print("COMPLETION STATUS:")
    print(f"  Total Templates: {summary['total_templates']}")
    print(f"  Translated: {summary['translated']['count']} ({summary['translated']['percentage']}%)")
    print(f"  Reviewed: {summary['reviewed']['count']} ({summary['reviewed']['percentage']}%)")
    print(f"  Published: {summary['published']['count']} ({summary['published']['percentage']}%)")
    print(f"  Draft: {summary['draft']['count']} ({summary['draft']['percentage']}%)")
    print(f"  Stale: {summary['stale']['count']} ({summary['stale']['percentage']}%)")

    print("\nCOMPLETION METRICS:")
    metrics = report["completion_metrics"]
    print(f"  Overall Completion: {metrics['overall_completion']}%")
    print(f"  Ready to Publish: {metrics['ready_to_publish']} templates")
    print(f"  Urgent Actions Needed: {metrics['urgent_actions']} templates")

    print("\nACTION ITEMS:")

    needs_trans = report["needs_translation"]
    if needs_trans["count"] > 0:
        print(f"\n  ⚠️  Needs Translation ({needs_trans['count']}):")
        for template in needs_trans["templates"][:5]:
            print(f"    - {template['template_key']}")
        if needs_trans["count"] > 5:
            print(f"    ... and {needs_trans['count'] - 5} more")

    needs_review = report["needs_review"]
    if needs_review["count"] > 0:
        print(f"\n  🔍 Needs Review ({needs_review['count']}):")
        for template in needs_review["templates"][:5]:
            print(f"    - {template['template_key']}")
        if needs_review["count"] > 5:
            print(f"    ... and {needs_review['count'] - 5} more")

    stale = report["stale_translations"]
    if stale["count"] > 0:
        print(f"\n  🔄 Stale Translations ({stale['count']}):")
        for template in stale["templates"][:5]:
            print(f"    - {template['template_key']} (stale since {template['stale_since']})")
        if stale["count"] > 5:
            print(f"    ... and {stale['count'] - 5} more")

    print("\n" + "="*80 + "\n")


async def main():
    """Main entry point for report generation."""
    print("Generating translation audit report...")

    try:
        report = await generate_translation_report()

        # Print summary
        print_report_summary(report)

        # Save to file
        filepath = await save_report_to_file(report)
        print(f"Report saved to: {filepath}")

        return report

    except Exception as e:
        print(f"Error generating report: {e}")
        raise


if __name__ == "__main__":
    report = asyncio.run(main())
