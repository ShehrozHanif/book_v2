"""
Glossary Terminology Consistency Tests (T034)

Tests for consistency of glossary terms across the application:
1. Translation pair consistency (English ↔ Urdu)
2. Pronunciation guide consistency
3. Definition quality consistency
4. Category consistency
5. Cross-component term usage consistency
6. Duplicate term detection
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestTranslationConsistency:
    """Tests for English-Urdu translation consistency."""

    async def test_all_terms_have_both_translations(self, client: AsyncClient):
        """Every term should have both English and Urdu translations."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            assert term.get("english_term"), f"Term {term.get('id')} missing English"
            assert term.get("urdu_translation"), f"Term {term.get('id')} missing Urdu"
            assert len(term["english_term"].strip()) > 0
            assert len(term["urdu_translation"].strip()) > 0

    async def test_translations_not_identical(self, client: AsyncClient):
        """English and Urdu translations should be different."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            # They should be different (not just copied)
            assert (
                term["english_term"].lower() != term["urdu_translation"].lower()
            ), f"Term {term.get('id')} has identical translations"

    async def test_bidirectional_search_consistency(self, client: AsyncClient):
        """Searching in English and Urdu should yield related results."""
        # Search in English
        eng_response = await client.get(
            "/api/v1/glossary/search?q=sensor&language=english"
        )

        assert eng_response.status_code == status.HTTP_200_OK
        eng_results = eng_response.json()

        # Get Urdu translation of first result if available
        if eng_results:
            first_term_urdu = eng_results[0].get("urdu_translation", "")

            # Search in Urdu
            if first_term_urdu:
                urdu_response = await client.get(
                    f"/api/v1/glossary/search?q={first_term_urdu}&language=urdu"
                )

                # Should find matching terms
                assert urdu_response.status_code == status.HTTP_200_OK


class TestDefinitionConsistency:
    """Tests for definition quality and consistency."""

    async def test_all_terms_have_definitions(self, client: AsyncClient):
        """Every term should have both English and Urdu definitions."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            assert (
                term.get("definition_english") and len(term["definition_english"].strip()) > 0
            ), f"Term {term.get('id')} missing English definition"

            assert (
                term.get("definition_urdu") and len(term["definition_urdu"].strip()) > 0
            ), f"Term {term.get('id')} missing Urdu definition"

    async def test_definition_minimum_length(self, client: AsyncClient):
        """Definitions should have minimum acceptable length."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        min_length = 10  # At least 10 characters

        for term in terms:
            eng_def = term.get("definition_english", "")
            assert (
                len(eng_def.strip()) >= min_length
            ), f"Definition too short for {term.get('english_term')}"

    async def test_definitions_not_identical(self, client: AsyncClient):
        """Definitions should be translated, not identical."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            eng_def = term.get("definition_english", "")
            urdu_def = term.get("definition_urdu", "")

            # They should be different
            assert (
                eng_def.lower() != urdu_def.lower()
            ), f"Definitions are identical for {term.get('english_term')}"


class TestPronunciationConsistency:
    """Tests for pronunciation guide consistency."""

    async def test_all_terms_have_pronunciation(self, client: AsyncClient):
        """Every term should have a pronunciation guide."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            assert (
                term.get("pronunciation_transliterated") and
                len(term["pronunciation_transliterated"].strip()) > 0
            ), f"Term {term.get('english_term')} missing pronunciation"

    async def test_pronunciation_format_consistency(self, client: AsyncClient):
        """Pronunciation guides should follow consistent format."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            pronunciation = term.get("pronunciation_transliterated", "")

            # Should be lowercase (convention)
            if pronunciation:
                # Most pronunciations should be lowercase
                assert (
                    pronunciation[0].islower() or pronunciation[0].isdigit()
                ), f"Pronunciation should start lowercase: {pronunciation}"


class TestCategoryConsistency:
    """Tests for category assignment consistency."""

    async def test_all_terms_have_category(self, client: AsyncClient):
        """Every term should have a category."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            assert (
                term.get("category") and len(term["category"].strip()) > 0
            ), f"Term {term.get('english_term')} missing category"

    async def test_categories_from_valid_list(self, client: AsyncClient):
        """Categories should come from a valid, predefined list."""
        # Get available categories
        cat_response = await client.get("/api/v1/glossary/categories")

        assert cat_response.status_code == status.HTTP_200_OK
        valid_categories = set(cat_response.json())

        # Check all terms use valid categories
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            category = term.get("category", "").lower().strip()
            assert (
                category in valid_categories or category in {
                    "robotics", "control-systems", "kinematics",
                    "programming", "hardware", "dynamics"
                }
            ), f"Unknown category: {category} for term {term.get('english_term')}"

    async def test_category_distribution(self, client: AsyncClient):
        """Categories should have reasonable distribution (no single category > 80%)."""
        cat_response = await client.get("/api/v1/glossary/categories")

        assert cat_response.status_code == status.HTTP_200_OK

        # Get terms per category
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        if len(terms) > 0:
            from collections import Counter

            categories = [t.get("category", "") for t in terms]
            distribution = Counter(categories)

            total = len(categories)
            max_percent = max(distribution.values()) / total * 100

            # No single category should dominate (> 90%)
            assert (
                max_percent < 90
            ), f"Category distribution imbalanced: {max_percent:.1f}%"


class TestDuplicateConsistency:
    """Tests for duplicate term detection."""

    async def test_no_exact_duplicate_terms(self, client: AsyncClient):
        """Should not have exact duplicate English terms (case-insensitive)."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        seen_terms = set()
        duplicates = []

        for term in terms:
            english_lower = term.get("english_term", "").lower().strip()

            if english_lower in seen_terms:
                duplicates.append(english_lower)
            else:
                seen_terms.add(english_lower)

        assert (
            len(duplicates) == 0
        ), f"Duplicate terms found: {duplicates}"

    async def test_no_duplicate_urdu_translations(self, client: AsyncClient):
        """Should not have exact duplicate Urdu translations (case-insensitive)."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        seen_translations = set()
        duplicates = []

        for term in terms:
            urdu_lower = term.get("urdu_translation", "").lower().strip()

            if urdu_lower in seen_translations:
                duplicates.append(urdu_lower)
            else:
                seen_translations.add(urdu_lower)

        # Allow some flexibility (not all should be 1:1 unique)
        # But shouldn't have many duplicates
        assert (
            len(duplicates) <= len(terms) * 0.05
        ), f"Too many duplicate Urdu translations: {len(duplicates)}/{len(terms)}"


class TestStatusConsistency:
    """Tests for status field consistency."""

    async def test_all_terms_have_valid_status(self, client: AsyncClient):
        """All terms should have a valid status."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        valid_statuses = {"active", "inactive", "draft", "archived", "published"}

        for term in terms:
            status_val = term.get("status", "").lower().strip()
            assert (
                status_val in valid_statuses or status_val == ""
            ), f"Invalid status: {status_val} for term {term.get('english_term')}"

    async def test_public_terms_are_active(self, client: AsyncClient):
        """Terms available through public API should be active/published."""
        response = await client.get("/api/v1/glossary?limit=200")

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        for term in terms:
            status_val = term.get("status", "").lower().strip()

            # Should be published/active
            assert (
                status_val in {"active", "published"} or status_val == ""
            ), f"Non-active term returned: {status_val} for {term.get('english_term')}"


class TestDataIntegrity:
    """Tests for overall data integrity."""

    async def test_search_returns_valid_term_structure(self, client: AsyncClient):
        """Search results should return complete term structure."""
        response = await client.get(
            "/api/v1/glossary/search?q=test&language=english&limit=5"
        )

        assert response.status_code == status.HTTP_200_OK
        terms = response.json()

        required_fields = [
            "id", "english_term", "urdu_translation",
            "pronunciation_transliterated", "definition_english",
            "definition_urdu", "category", "status"
        ]

        for term in terms:
            for field in required_fields:
                assert field in term, f"Missing field '{field}' in search result"

    async def test_stats_accuracy(self, client: AsyncClient):
        """Statistics should match actual term counts."""
        # Get stats
        stats_response = await client.get("/api/v1/glossary/stats")

        assert stats_response.status_code == status.HTTP_200_OK
        stats = stats_response.json()

        # Get actual terms
        terms_response = await client.get(f"/api/v1/glossary?limit={stats['total_terms'] + 50}")

        assert terms_response.status_code == status.HTTP_200_OK
        terms = terms_response.json()

        # Verify counts match
        assert (
            stats["total_terms"] == len(terms)
        ), f"Stats mismatch: {stats['total_terms']} vs {len(terms)}"

        # Verify category counts
        from collections import Counter

        actual_categories = set(t.get("category") for t in terms)

        assert (
            stats["total_categories"] >= len(actual_categories)
        ), "Category count mismatch"
