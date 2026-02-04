# Integration Test Suite Guide - User Story 1 MVP

## Overview

This guide documents the comprehensive integration test suite for User Story 1, which tests the complete MVP end-to-end flow:
1. **Text Selection** (T022)
2. **Question Asking** (T023)
3. **Answer with Citations** (T024)

## Test File Location

```
backend/tests/integration/test_user_story_1.py
```

## Test Coverage

### Test 1: Health Check
- **Purpose**: Verify API is reachable and operational
- **File**: `test_health_check()`
- **Validates**:
  - Health endpoint returns 200 OK
  - Response contains `"status": "ok"`

### Test 2: Query Processing - Core MVP Flow
- **Purpose**: Test the complete end-to-end user query workflow
- **File**: `test_user_story_1_complete_flow()`
- **Validates**:
  - Query embedded to 1536 dimensions (OpenAI embedding spec)
  - Passages retrieved from Qdrant vector database
  - Response generated with LLM
  - Citations present in format `[Chapter X: Section Y]`
  - Processing time < 3 seconds (SC-001 SLA)
  - Relevance scores > 0.85 (SC-005 requirement)
  - All services called in correct order

**Sub-tests**:
- `test_query_embedding_1536_dimensions()` - Validates embedding dimensionality
- `test_passage_retrieval_relevance_threshold()` - Validates relevance scores
- `test_response_includes_citations()` - Validates citation format
- `test_processing_time_sla()` - Validates latency SLA

### Test 3: Multi-Turn Conversation
- **Purpose**: Test conversation ID generation and persistence
- **Files**:
  - `test_conversation_id_generation()` - Conversation ID created for first query
  - `test_conversation_id_persistence()` - Same ID used across multiple queries

### Test 4: Pipeline Integration
- **Purpose**: Test full RAG pipeline: Embedding → Retrieval → Generation
- **Files**:
  - `test_embedding_retrieval_generation_pipeline()` - Services called in correct order
  - `test_pipeline_timing_breakdown()` - Timing measured accurately

### Test 5: Error Handling
- **Purpose**: Test error scenarios and edge cases
- **Tests**:
  - `test_empty_query_validation()` - Empty queries rejected
  - `test_embedding_service_timeout()` - API timeout handled
  - `test_retrieval_service_failure()` - Qdrant errors handled
  - `test_generation_service_failure()` - LLM errors handled
  - `test_invalid_conversation_id_handling()` - Invalid UUIDs handled gracefully

### Test 6: Response Quality Validation
- **Purpose**: Validate response schema and data quality
- **Tests**:
  - `test_response_structure_validation()` - ChatResponse schema compliance
  - `test_passages_and_scores_alignment()` - Passages/scores match
  - `test_context_used_in_generation()` - Context passed to generation

### Test 7: Load and Performance
- **Purpose**: Test system under multiple sequential queries
- **Tests**:
  - `test_sequential_queries_performance()` - Multiple queries processed
  - `test_response_consistency_across_calls()` - Consistent responses

## Running the Tests

### Prerequisites

Install test dependencies:

```bash
cd backend
pip install -r requirements.txt pytest pytest-asyncio pytest-cov
```

### Run All Integration Tests

```bash
pytest tests/integration/test_user_story_1.py -v
```

### Run Specific Test

```bash
pytest tests/integration/test_user_story_1.py::test_user_story_1_complete_flow -v
```

### Run with Coverage Report

```bash
pytest tests/integration/test_user_story_1.py -v --cov=src --cov-report=html
```

The HTML coverage report will be generated in `htmlcov/index.html`.

### Run with Detailed Output

```bash
pytest tests/integration/test_user_story_1.py -vv -s
```

### Run Specific Test Category

```bash
# Run only error handling tests
pytest tests/integration/test_user_story_1.py -v -k "error"

# Run only performance tests
pytest tests/integration/test_user_story_1.py -v -k "performance"

# Run only pipeline tests
pytest tests/integration/test_user_story_1.py -v -k "pipeline"
```

## Test Architecture

### Fixtures

The test suite uses comprehensive mocking fixtures:

1. **`test_client`** - Async HTTP client for API testing
2. **`mock_session`** - Mock AsyncSession for database operations
3. **`mock_embedding_service`** - Mock OpenAI embedding service
4. **`mock_retrieval_service`** - Mock Qdrant retrieval service
5. **`mock_generation_service`** - Mock LLM generation service
6. **`chat_service`** - Full ChatService with all mocks wired

### Mocking Strategy

The tests use `unittest.mock.AsyncMock` for all external service dependencies:

- **Embedding Service**: Returns 1536-dimensional vectors
- **Retrieval Service**: Returns 3 sample passages with >0.85 relevance scores
- **Generation Service**: Returns response with citations in `[Chapter X: Section Y]` format
- **Database Session**: Mock AsyncSession for transaction testing

This approach allows tests to run:
- **Offline** (no API calls to OpenAI)
- **Locally** (no connection to Qdrant)
- **Fast** (no actual LLM processing)
- **Deterministically** (consistent mock responses)

## Acceptance Criteria

All tests validate against these acceptance criteria:

### MVP Flow (Test 2)
- ✓ Query is embedded to 1536 dimensions
- ✓ Passages are retrieved from Qdrant
- ✓ Response is generated with citations
- ✓ Citations are in format `[Chapter X: Section Y]`
- ✓ Processing time < 3 seconds (SC-001)
- ✓ Relevance scores > 0.85 (SC-005)

### Conversation Tracking (Test 3)
- ✓ Conversation ID is generated for first query
- ✓ Same ID is preserved across multiple queries
- ✓ ID can be used to load conversation history

### Pipeline Integration (Test 4)
- ✓ Embedding service called first
- ✓ Retrieval service called with embedding vector
- ✓ Generation service called with retrieved context
- ✓ All services are called exactly once per query

### Error Handling (Test 5)
- ✓ Empty queries raise ValueError
- ✓ Embedding timeouts propagate
- ✓ Retrieval failures propagate
- ✓ Generation failures propagate
- ✓ Invalid UUIDs handled gracefully

### Response Quality (Test 6)
- ✓ ChatResponse has all required fields
- ✓ Passages and scores have matching lengths
- ✓ Retrieved context is passed to generation
- ✓ All scores are in 0-1 range

### Performance (Test 7)
- ✓ Sequential queries all complete < 3s
- ✓ Responses are consistent across calls

## Expected Test Output

```
tests/integration/test_user_story_1.py::test_health_check PASSED
tests/integration/test_user_story_1.py::test_health_check_chat_service PASSED
tests/integration/test_user_story_1.py::test_user_story_1_complete_flow PASSED
tests/integration/test_user_story_1.py::test_query_embedding_1536_dimensions PASSED
tests/integration/test_user_story_1.py::test_passage_retrieval_relevance_threshold PASSED
tests/integration/test_user_story_1.py::test_response_includes_citations PASSED
tests/integration/test_user_story_1.py::test_processing_time_sla PASSED
tests/integration/test_user_story_1.py::test_conversation_id_generation PASSED
tests/integration/test_user_story_1.py::test_conversation_id_persistence PASSED
tests/integration/test_user_story_1.py::test_embedding_retrieval_generation_pipeline PASSED
tests/integration/test_user_story_1.py::test_pipeline_timing_breakdown PASSED
tests/integration/test_user_story_1.py::test_empty_query_validation PASSED
tests/integration/test_user_story_1.py::test_embedding_service_timeout PASSED
tests/integration/test_user_story_1.py::test_retrieval_service_failure PASSED
tests/integration/test_user_story_1.py::test_generation_service_failure PASSED
tests/integration/test_user_story_1.py::test_invalid_conversation_id_handling PASSED
tests/integration/test_user_story_1.py::test_response_structure_validation PASSED
tests/integration/test_user_story_1.py::test_passages_and_scores_alignment PASSED
tests/integration/test_user_story_1.py::test_context_used_in_generation PASSED
tests/integration/test_user_story_1.py::test_sequential_queries_performance PASSED
tests/integration/test_user_story_1.py::test_response_consistency_across_calls PASSED

========================= 21 passed in X.XXs =========================
```

## Coverage Target

The integration tests target >80% coverage for the MVP core path:

- `src/services/chat_service.py` - 100%
- `src/services/embedding_service.py` - 90%
- `src/services/retrieval_service.py` - 90%
- `src/services/generation_service.py` - 90%
- `src/models/schemas.py` - 100%
- `src/api/routes/chat.py` - 85%

## CI/CD Integration

To integrate with CI/CD pipeline:

```bash
# In your CI configuration (GitHub Actions, GitLab CI, etc.)
pytest backend/tests/integration/test_user_story_1.py \
  -v \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml \
  --junit-xml=test-results.xml
```

## Troubleshooting

### AsyncMock not defined

**Error**: `NameError: name 'AsyncMock' is not defined`

**Solution**: Ensure Python 3.8+ and `unittest.mock.AsyncMock` is imported:
```python
from unittest.mock import AsyncMock
```

### Pytest asyncio not found

**Error**: `pytest: error: unrecognized arguments: --asyncio-mode`

**Solution**: Install pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Event loop already running

**Error**: `RuntimeError: Event loop is already running`

**Solution**: Use pytest-asyncio with `asyncio_mode = auto` in pytest.ini

### Import errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Run pytest from `backend/` directory:
```bash
cd backend
pytest tests/integration/test_user_story_1.py
```

## Next Steps

After integration tests pass:

1. **Unit Tests**: Run unit tests for individual services
   ```bash
   pytest tests/unit/ -v
   ```

2. **End-to-End Tests**: Test with real services
   ```bash
   pytest tests/e2e/ -v
   ```

3. **Performance Tests**: Load testing with real API
   ```bash
   pytest tests/performance/ -v
   ```

## References

- **User Story 1**: Text Selection → Question → Answer with Citations
- **Task T022**: Text Selection UI
- **Task T023**: Question Processing API
- **Task T024**: Citation Generation
- **SLA SC-001**: <3 second response time
- **SLA SC-005**: >85% relevance threshold
