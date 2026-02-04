# US2 & US3 Integration Tests - Quick Reference

## Overview

Comprehensive integration tests for User Story 2 (Multi-Turn Conversations) and User Story 3 (Edge Cases & Error Handling).

**Total Tests**: 24 (8 US2 + 16 US3)
**Test Status**: 100% Passing
**Coverage**: 41% (services layer)

---

## Quick Start

### Run All Tests
```bash
cd backend
pytest tests/integration/test_user_story_2_context.py tests/integration/test_user_story_3_edge_cases.py -v
```

### Run with Coverage Report
```bash
pytest tests/integration/test_user_story_2_context.py tests/integration/test_user_story_3_edge_cases.py -v --cov=src.services --cov-report=html
```

### View Coverage Report
```bash
# After running with --cov-report=html
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Test Suites

### US2: Multi-Turn Conversations (T041)
**File**: `test_user_story_2_context.py`
**Tests**: 8

```bash
# Run US2 tests only
pytest tests/integration/test_user_story_2_context.py -v

# Run specific US2 test
pytest tests/integration/test_user_story_2_context.py::test_multi_turn_conversation_five_exchanges -v
```

**Test List**:
1. `test_single_question_baseline` - Baseline single query
2. `test_follow_up_question_same_conversation` - Conversation ID persistence
3. `test_multi_turn_conversation_five_exchanges` - 5 exchanges with <3s SLA
4. `test_context_passed_to_generation_service` - Context loading
5. `test_message_history_persists_in_database` - Database persistence
6. `test_session_persistence_integration` - Frontend integration (doc)
7. `test_conversation_id_uuid_format` - UUID validation
8. `test_concurrent_conversations_isolated` - Isolation testing

### US3: Edge Cases (T048)
**File**: `test_user_story_3_edge_cases.py`
**Tests**: 16

```bash
# Run US3 tests only
pytest tests/integration/test_user_story_3_edge_cases.py -v

# Run specific US3 test
pytest tests/integration/test_user_story_3_edge_cases.py::test_injection_attempt_handling -v
```

**Test List**:
1. `test_empty_query_validation` - Empty query rejection
2. `test_whitespace_only_query_validation` - Whitespace handling
3. `test_injection_attempt_handling` - Prompt injection safety
4. `test_off_topic_query_low_relevance` - Off-topic detection
5. `test_embedding_api_timeout_handling` - Embedding timeout fallback
6. `test_generation_api_timeout_handling` - Generation timeout fallback
7. `test_retrieval_service_connection_failure` - Qdrant failure fallback
8. `test_generation_service_api_error` - LLM error fallback
9. `test_rate_limiting_simulation` - Rate limiting (doc)
10. `test_invalid_conversation_id_format` - Invalid UUID handling
11. `test_max_query_length_validation` - Max length enforcement
12. `test_max_query_length_boundary` - Boundary testing
13. `test_response_cites_retrieved_context_only` - Citation validation
14. `test_no_unhandled_exceptions_stress_test` - Stress testing
15. `test_concurrent_requests_no_race_conditions` - Concurrency testing
16. `test_database_transaction_rollback_on_error` - Rollback verification

---

## Test Filtering

### Run Tests by Pattern
```bash
# All timeout tests
pytest tests/integration/ -v -k "timeout"

# All validation tests
pytest tests/integration/ -v -k "validation"

# All conversation tests
pytest tests/integration/ -v -k "conversation"

# All stress/concurrency tests
pytest tests/integration/ -v -k "stress or concurrent"
```

### Run by Test Number
```bash
# Run first 3 US2 tests
pytest tests/integration/test_user_story_2_context.py::test_single_question_baseline tests/integration/test_user_story_2_context.py::test_follow_up_question_same_conversation tests/integration/test_user_story_2_context.py::test_multi_turn_conversation_five_exchanges -v
```

---

## Debugging

### Run with Verbose Output
```bash
pytest tests/integration/test_user_story_2_context.py -vv
```

### Run with Print Statements
```bash
pytest tests/integration/test_user_story_2_context.py -v -s
```

### Run with Full Traceback
```bash
pytest tests/integration/test_user_story_2_context.py -v --tb=long
```

### Run Single Test with All Debug Info
```bash
pytest tests/integration/test_user_story_3_edge_cases.py::test_injection_attempt_handling -vv -s --tb=long
```

---

## Performance Testing

### Run with Timing
```bash
pytest tests/integration/ -v --durations=10
```

### Run with Performance Profiling
```bash
pytest tests/integration/ -v --profile
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run US2 & US3 Integration Tests
  run: |
    cd backend
    pytest tests/integration/test_user_story_2_context.py tests/integration/test_user_story_3_edge_cases.py -v --cov=src.services --cov-report=xml

- name: Upload Coverage Report
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

### GitLab CI Example
```yaml
test_us2_us3:
  stage: test
  script:
    - cd backend
    - pytest tests/integration/test_user_story_2_context.py tests/integration/test_user_story_3_edge_cases.py -v --cov=src.services --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Test Maintenance

### Update Test Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Check Test Health
```bash
# Run tests in random order to detect dependencies
pytest tests/integration/ --random-order

# Run tests with coverage threshold
pytest tests/integration/ --cov=src.services --cov-fail-under=40
```

---

## Common Issues

### Issue: Tests hang
**Solution**: Check for unawaited async calls
```bash
pytest tests/integration/ -v -W error::RuntimeWarning
```

### Issue: Mock not working
**Solution**: Verify mock patch path
```python
# Correct: patch where it's used, not where it's defined
with patch('src.services.chat_service.get_conversation_service'):
    ...
```

### Issue: Database conflicts
**Solution**: Use in-memory SQLite for tests
```python
# conftest.py already configured with sqlite+aiosqlite:///:memory:
```

---

## Test Data

### Mock Responses
- **Embedding**: 1536-dimensional vectors (all 0.1)
- **Retrieval**: 3 passages with scores [0.95, 0.87, 0.86]
- **Generation**: "Answer [Chapter X]"

### Test Queries
- Standard: "What is ROS 2?"
- Edge cases: Empty, whitespace, injection attempts, off-topic
- Stress: Unicode, special chars, very long

---

## Documentation

### Full Test Report
See: `T041_T048_TEST_REPORT.md`

### Coverage Report
After running with `--cov-report=html`, view: `htmlcov/index.html`

### Test Logs
Structured logs available in console output during test runs

---

## Next Steps

1. **E2E Tests**: Implement frontend sessionStorage tests with Cypress
2. **Load Tests**: Add performance tests for high-concurrency scenarios
3. **Security Tests**: Add dedicated security scan suite
4. **Live Integration**: Create separate suite for actual API integration

---

## Support

For test issues or questions, refer to:
- Test Report: `T041_T048_TEST_REPORT.md`
- Test Code: Review inline documentation in test files
- Coverage: Check `htmlcov/index.html` for detailed coverage analysis

**Last Updated**: 2026-01-30
**Pytest Version**: 9.0.2
**Python Version**: 3.14.2
