"""
Performance Testing for Urdu Translation Feature (T066)

Verifies:
- Chatbot response time <3 seconds with translation lookup
- Language toggle <1 second
- Glossary search <500ms
"""

import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.main import app
from backend.src.personalization.models.db_models import (
    ChatbotResponseTemplate,
    ChatbotTranslation,
    GlossaryTerm,
    UserLanguagePreference,
)
from backend.src.personalization.services.chatbot_translation_service import ChatbotTranslationService
from backend.src.personalization.services.glossary_service import GlossaryService
from backend.src.personalization.services.language_preference_service import LanguagePreferenceService


class TestPerformanceMetrics:
    """Performance tests for translation feature."""

    @pytest.mark.asyncio
    async def test_chatbot_response_time_under_3_seconds(self, test_db: AsyncSession):
        """Verify chatbot response time is under 3 seconds with translation lookup."""
        # Setup: Create test template and translation
        template = ChatbotResponseTemplate(
            key="greeting",
            english_content="Hello, how can I help you?",
            created_at=None,
        )
        test_db.add(template)
        await test_db.flush()

        translation = ChatbotTranslation(
            template_id=template.id,
            urdu_translation="السلام علیکم، میں آپ کی کیا مدد کر سکتا ہوں؟",
            created_at=None,
        )
        test_db.add(translation)
        await test_db.commit()

        # Test: Measure response retrieval time
        service = ChatbotTranslationService(test_db)

        start_time = time.time()
        response = await service.get_response("greeting", "urdu")
        elapsed_time = time.time() - start_time

        # Assert: Response time under 3 seconds
        assert elapsed_time < 3.0, f"Response time {elapsed_time:.2f}s exceeds 3s limit"
        assert response is not None
        assert "السلام" in response

    @pytest.mark.asyncio
    async def test_language_toggle_time_under_1_second(self, test_db: AsyncSession):
        """Verify language toggle operation completes in under 1 second."""
        from uuid import uuid4

        user_id = uuid4()

        # Test: Measure language preference update time
        service = LanguagePreferenceService(test_db)

        start_time = time.time()
        await service.set_preference(user_id, "urdu")
        elapsed_time = time.time() - start_time

        # Assert: Toggle time under 1 second
        assert elapsed_time < 1.0, f"Toggle time {elapsed_time:.2f}s exceeds 1s limit"

        # Verify preference was set
        pref = await service.get_preference(user_id)
        assert pref == "urdu"

    @pytest.mark.asyncio
    async def test_glossary_search_time_under_500ms(self, test_db: AsyncSession):
        """Verify glossary search completes in under 500ms."""
        # Setup: Create test glossary terms
        terms = [
            GlossaryTerm(
                english_term=f"Term {i}",
                urdu_translation=f"اردو ترجمہ {i}",
                pronunciation_transliterated=f"term_{i}",
                definition_english=f"Definition {i}",
                definition_urdu=f"تعریف {i}",
            )
            for i in range(50)
        ]
        test_db.add_all(terms)
        await test_db.commit()

        # Test: Measure search time
        service = GlossaryService(test_db)

        start_time = time.time()
        results = await service.search_terms("Term", language="english")
        elapsed_time = time.time() - start_time

        # Assert: Search time under 500ms
        assert elapsed_time < 0.5, f"Search time {elapsed_time*1000:.2f}ms exceeds 500ms limit"
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_batch_response_retrieval_performance(self, test_db: AsyncSession):
        """Verify retrieving 10 responses takes less than 5 seconds total."""
        # Setup: Create multiple templates
        templates = [
            ChatbotResponseTemplate(
                key=f"template_{i}",
                english_content=f"English content {i}",
                created_at=None,
            )
            for i in range(10)
        ]
        test_db.add_all(templates)
        await test_db.flush()

        translations = [
            ChatbotTranslation(
                template_id=template.id,
                urdu_translation=f"اردو مواد {i}",
                created_at=None,
            )
            for i, template in enumerate(templates)
        ]
        test_db.add_all(translations)
        await test_db.commit()

        # Test: Measure batch retrieval time
        service = ChatbotTranslationService(test_db)

        start_time = time.time()
        responses = []
        for i in range(10):
            response = await service.get_response(f"template_{i}", "urdu")
            responses.append(response)
        elapsed_time = time.time() - start_time

        # Assert: All responses retrieved in under 5 seconds
        assert elapsed_time < 5.0, f"Batch retrieval time {elapsed_time:.2f}s exceeds 5s limit"
        assert len(responses) == 10
        assert all(resp is not None for resp in responses)

    @pytest.mark.asyncio
    async def test_cache_hit_performance(self, test_db: AsyncSession):
        """Verify cached response retrieval is significantly faster."""
        # Setup: Create template and translation
        template = ChatbotResponseTemplate(
            key="cached_test",
            english_content="Cached content",
            created_at=None,
        )
        test_db.add(template)
        await test_db.flush()

        translation = ChatbotTranslation(
            template_id=template.id,
            urdu_translation="محفوظ مواد",
            created_at=None,
        )
        test_db.add(translation)
        await test_db.commit()

        service = ChatbotTranslationService(test_db)

        # First call (cache miss)
        start_time = time.time()
        await service.get_response("cached_test", "urdu")
        first_call_time = time.time() - start_time

        # Second call (cache hit) - should be faster
        start_time = time.time()
        await service.get_response("cached_test", "urdu")
        second_call_time = time.time() - start_time

        # Assert: Cache hit is significantly faster (at least 50% faster)
        assert second_call_time < first_call_time * 0.5 or second_call_time < 0.01, \
            f"Cache hit not significantly faster: {first_call_time:.4f}s vs {second_call_time:.4f}s"

    @pytest.mark.asyncio
    async def test_large_glossary_search_performance(self, test_db: AsyncSession):
        """Verify search performance with large glossary (1000+ terms)."""
        # Setup: Create large glossary
        terms = [
            GlossaryTerm(
                english_term=f"Term_{i:04d}",
                urdu_translation=f"اردو_{i:04d}",
                pronunciation_transliterated=f"term_{i}",
                definition_english=f"Definition {i}",
                definition_urdu=f"تعریف {i}",
            )
            for i in range(1000)
        ]
        test_db.add_all(terms)
        await test_db.commit()

        service = GlossaryService(test_db)

        start_time = time.time()
        results = await service.search_terms("Term_00", language="english")
        elapsed_time = time.time() - start_time

        # Assert: Large search still under 1 second
        assert elapsed_time < 1.0, f"Large search time {elapsed_time:.2f}s exceeds 1s limit"
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_concurrent_language_toggle_performance(self, test_db: AsyncSession):
        """Verify concurrent language toggles maintain performance."""
        from uuid import uuid4
        import asyncio

        service = LanguagePreferenceService(test_db)

        # Create test users
        user_ids = [uuid4() for _ in range(10)]

        # Test: Concurrent toggles
        start_time = time.time()
        tasks = [
            service.set_preference(uid, "urdu" if i % 2 == 0 else "english")
            for i, uid in enumerate(user_ids)
        ]
        await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time

        # Assert: 10 concurrent toggles under 2 seconds
        assert elapsed_time < 2.0, f"Concurrent toggle time {elapsed_time:.2f}s exceeds 2s limit"


class TestPerformanceMetricsIntegration:
    """Integration tests for performance under realistic scenarios."""

    def test_api_response_time_endpoint(self, client: TestClient, auth_token: str):
        """Verify API endpoint response time with translation."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        start_time = time.time()
        response = client.get(
            "/api/v1/chatbot/languages",
            headers=headers,
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 0.5, f"API response time {elapsed_time:.2f}s exceeds 0.5s limit"

    def test_language_preference_endpoint_performance(self, client: TestClient, auth_token: str):
        """Verify language preference endpoint response time."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        start_time = time.time()
        response = client.put(
            "/api/v1/users/me/language-preference",
            headers=headers,
            json={"language": "urdu"},
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 0.5, f"Preference update time {elapsed_time:.2f}s exceeds 0.5s limit"

    def test_glossary_search_endpoint_performance(self, client: TestClient, auth_token: str):
        """Verify glossary search endpoint response time."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        start_time = time.time()
        response = client.get(
            "/api/v1/glossary/search?q=term&language=english",
            headers=headers,
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 0.5, f"Search response time {elapsed_time:.2f}s exceeds 0.5s limit"


class TestMemoryUsage:
    """Tests for memory efficiency."""

    @pytest.mark.asyncio
    async def test_cache_memory_footprint(self, test_db: AsyncSession):
        """Verify cache doesn't consume excessive memory."""
        import sys

        service = ChatbotTranslationService(test_db)

        # Create templates
        templates = [
            ChatbotResponseTemplate(
                key=f"mem_test_{i}",
                english_content=f"Content {i}" * 100,  # Large content
                created_at=None,
            )
            for i in range(100)
        ]
        test_db.add_all(templates)
        await test_db.flush()

        translations = [
            ChatbotTranslation(
                template_id=template.id,
                urdu_translation=f"مواد {i}" * 100,
                created_at=None,
            )
            for i, template in enumerate(templates)
        ]
        test_db.add_all(translations)
        await test_db.commit()

        # Populate cache
        initial_size = sys.getsizeof(service.cache)
        for i in range(100):
            await service.get_response(f"mem_test_{i}", "urdu")
        final_size = sys.getsizeof(service.cache)

        # Assert: Memory increase is reasonable (less than 10MB)
        memory_increase = (final_size - initial_size) / 1024 / 1024
        assert memory_increase < 10.0, f"Cache memory increase {memory_increase:.2f}MB exceeds 10MB limit"


class TestPerformanceBenchmarks:
    """Benchmarking tests for documented performance targets."""

    CHATBOT_RESPONSE_TARGET = 3.0  # seconds
    LANGUAGE_TOGGLE_TARGET = 1.0  # seconds
    GLOSSARY_SEARCH_TARGET = 0.5  # seconds

    @pytest.mark.asyncio
    async def test_performance_targets_met(self, test_db: AsyncSession):
        """Verify all performance targets are met."""
        results = {
            "chatbot_response_time": None,
            "language_toggle_time": None,
            "glossary_search_time": None,
        }

        # Test chatbot response
        template = ChatbotResponseTemplate(
            key="bench_test",
            english_content="Test",
            created_at=None,
        )
        test_db.add(template)
        await test_db.flush()

        translation = ChatbotTranslation(
            template_id=template.id,
            urdu_translation="ٹیسٹ",
            created_at=None,
        )
        test_db.add(translation)
        await test_db.commit()

        service = ChatbotTranslationService(test_db)
        start = time.time()
        await service.get_response("bench_test", "urdu")
        results["chatbot_response_time"] = time.time() - start

        # Test language toggle
        from uuid import uuid4
        pref_service = LanguagePreferenceService(test_db)
        start = time.time()
        await pref_service.set_preference(uuid4(), "urdu")
        results["language_toggle_time"] = time.time() - start

        # Test glossary search
        term = GlossaryTerm(
            english_term="Benchmark",
            urdu_translation="معیار",
            pronunciation_transliterated="measure",
            definition_english="A standard",
            definition_urdu="ایک معیار",
        )
        test_db.add(term)
        await test_db.commit()

        glossary_service = GlossaryService(test_db)
        start = time.time()
        await glossary_service.search_terms("Benchmark", language="english")
        results["glossary_search_time"] = time.time() - start

        # Assert: All targets met
        assert results["chatbot_response_time"] < self.CHATBOT_RESPONSE_TARGET, \
            f"Chatbot response {results['chatbot_response_time']:.2f}s exceeds {self.CHATBOT_RESPONSE_TARGET}s"
        assert results["language_toggle_time"] < self.LANGUAGE_TOGGLE_TARGET, \
            f"Language toggle {results['language_toggle_time']:.2f}s exceeds {self.LANGUAGE_TOGGLE_TARGET}s"
        assert results["glossary_search_time"] < self.GLOSSARY_SEARCH_TARGET, \
            f"Glossary search {results['glossary_search_time']:.2f}s exceeds {self.GLOSSARY_SEARCH_TARGET}s"
