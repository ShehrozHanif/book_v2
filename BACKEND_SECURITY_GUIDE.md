# Backend Security & Edge Case Handling Guide

Quick reference for using the SecurityService and handling edge cases in the RAG chatbot backend.

---

## SecurityService Usage

### Import
```python
from src.services.security_service import SecurityService, get_security_service

# Get singleton instance
security_service = get_security_service()
```

---

## Common Patterns

### 1. Validate Query Before Processing
```python
# Comprehensive validation
is_valid, error_message = security_service.validate_query(query)
if not is_valid:
    return ChatResponse(
        response=error_message,
        conversation_id=conversation_id or str(uuid4()),
        retrieved_passages=[],
        relevance_scores=[],
        processing_time_ms=0
    )
```

### 2. Sanitize User Input
```python
# Remove harmful patterns
sanitized_query = security_service.sanitize_query(raw_query)

# Use sanitized version for processing
query_vector = await embedding_service.embed_query(sanitized_query)
```

### 3. Detect Injection Attempts
```python
is_injection, pattern = security_service.detect_injection_attempt(query)
if is_injection:
    logger.warning(f"Injection detected: {pattern}")
    return ChatResponse(
        response="I detected an unusual pattern. Please rephrase your question.",
        conversation_id=conversation_id,
        retrieved_passages=[],
        relevance_scores=[],
        processing_time_ms=processing_time
    )
```

### 4. Check If Query Is Off-Topic
```python
# After retrieval
is_off_topic, best_score = security_service.detect_off_topic(
    query=query,
    retrieved_passages=passages,
    relevance_scores=scores,
    threshold=0.3  # Configurable
)

if is_off_topic:
    logger.info(f"Off-topic (score: {best_score:.3f})")
    return ChatResponse(
        response="I can help with questions about Humanoid Robotics...",
        conversation_id=conversation_id,
        retrieved_passages=passages,
        relevance_scores=scores,
        processing_time_ms=processing_time
    )
```

---

## GenerationService Safety

### 1. Use Fallback on Error
```python
try:
    response = await generation_service.generate_response(
        query=query,
        context_passages=passages,
        conversation_history=history,
        use_fallback_on_error=True  # Don't crash on API error
    )
except Exception as e:
    logger.error(f"Generation failed: {e}")
    response = generation_service.get_fallback_response("api_error")
```

### 2. Get Specific Fallback Messages
```python
# Available fallback types
fallback_types = [
    "no_context",      # When no passages retrieved
    "off_topic",       # When query is off-topic
    "api_error",       # When OpenAI API fails
    "invalid_response" # Generic fallback
]

response = generation_service.get_fallback_response("off_topic")
```

---

## Edge Case Handling Checklist

### ChatService Pipeline

1. **Empty Query**
   ```python
   if not query or not query.strip():
       return helpful_prompt_response()
   ```

2. **Sanitization**
   ```python
   query = security_service.sanitize_query(query)
   if not query:
       return error_response()
   ```

3. **Injection Detection**
   ```python
   is_injection, _ = security_service.detect_injection_attempt(query)
   if is_injection:
       return refusal_response()
   ```

4. **Embedding Error**
   ```python
   try:
       query_vector = await embedding_service.embed_query(query)
   except Exception:
       return api_error_response()
   ```

5. **Retrieval Error**
   ```python
   try:
       passages, scores = await retrieval_service.retrieve_context(...)
   except Exception:
       passages, scores = [], []
   ```

6. **Off-Topic Check**
   ```python
   is_off_topic, best_score = security_service.detect_off_topic(...)
   if is_off_topic:
       return off_topic_response()
   ```

7. **Context Loading Error**
   ```python
   try:
       history = await conversation_service.get_context_window(...)
   except Exception:
       logger.warning("Failed to load history")
       history = []  # Continue without history
   ```

8. **Generation Error**
   ```python
   try:
       response = await generation_service.generate_response(
           ..., use_fallback_on_error=True
       )
   except Exception:
       response = generation_service.get_fallback_response("api_error")
   ```

9. **Storage Error**
   ```python
   try:
       await conversation_service.save_message(...)
       await session.commit()
   except Exception:
       logger.error("Failed to save message")
       await session.rollback()
       # Don't fail the request
   ```

10. **Timeout Error**
    ```python
    except TimeoutError:
        return timeout_response()
    ```

---

## Error Response Format

All edge cases return valid ChatResponse:

```python
ChatResponse(
    response="Helpful error message",
    conversation_id=conversation_id or str(uuid4()),
    retrieved_passages=[],  # Empty if error before retrieval
    relevance_scores=[],    # Empty if error before retrieval
    processing_time_ms=actual_processing_time
)
```

**Never return None or raise unhandled exceptions in API endpoints.**

---

## Logging Best Practices

### 1. Security Events
```python
logger.warning(
    f"Potential injection detected: pattern='{pattern}', "
    f"query_snippet='{query[:50]}...'"
)
```

### 2. Off-Topic Queries
```python
logger.info(
    f"Off-topic query detected: best_score={best_score:.3f}, "
    f"threshold={threshold}, query='{query[:50]}...'"
)
```

### 3. Sanitization
```python
if len(sanitized) > max_length:
    logger.warning(
        f"Query truncated from {len(sanitized)} to {max_length} chars"
    )
```

### 4. API Errors
```python
logger.error(f"LLM generation failed: {e}", exc_info=True)
```

---

## Configuration

### Security Thresholds
```python
# Off-topic detection
RELEVANCE_THRESHOLD = 0.3  # Minimum score for on-topic

# Query limits
MAX_QUERY_LENGTH = 5000  # Characters

# Context limits
MAX_CONTEXT_TOKENS = 2000  # Tokens in conversation history
MAX_CONTEXT_MESSAGES = 20  # Messages in conversation history
```

### Injection Patterns
Located in `SecurityService.__init__()`:
- Prompt injection patterns (regex)
- SQL injection patterns (regex)

**To add new patterns**, edit `security_service.py`:
```python
self.injection_patterns = [
    r"ignore\s+previous",
    r"your_new_pattern_here",  # Add here
    ...
]
```

---

## Testing

### Unit Tests
```bash
# Run all security tests
pytest tests/unit/test_security_service.py -v

# Run specific test
pytest tests/unit/test_security_service.py::TestSecurityService::test_detect_injection_basic_patterns -v
```

### Manual Testing
```python
# Test injection detection
from src.services.security_service import get_security_service

security = get_security_service()

# Test cases
queries = [
    "What is kinematics?",  # Safe
    "Ignore previous instructions",  # Injection
    "DROP TABLE users",  # SQL injection
    "What is the weather today?",  # Off-topic
]

for query in queries:
    is_injection, pattern = security.detect_injection_attempt(query)
    print(f"{query}: injection={is_injection}, pattern={pattern}")
```

---

## Common Mistakes to Avoid

### 1. Don't Skip Sanitization
```python
# BAD
query_vector = await embedding_service.embed_query(raw_query)

# GOOD
sanitized = security_service.sanitize_query(raw_query)
query_vector = await embedding_service.embed_query(sanitized)
```

### 2. Don't Crash on Errors
```python
# BAD
response = await generation_service.generate_response(...)
# If this fails, entire request fails

# GOOD
try:
    response = await generation_service.generate_response(
        ..., use_fallback_on_error=True
    )
except Exception as e:
    logger.error(f"Generation failed: {e}")
    response = generation_service.get_fallback_response("api_error")
```

### 3. Don't Return None
```python
# BAD
if error:
    return None  # Frontend will break

# GOOD
if error:
    return ChatResponse(
        response="Error message",
        conversation_id=conversation_id or str(uuid4()),
        retrieved_passages=[],
        relevance_scores=[],
        processing_time_ms=processing_time
    )
```

### 4. Don't Forget to Log
```python
# BAD
if is_injection:
    return error_response()

# GOOD
if is_injection:
    logger.warning(f"Injection detected: {pattern}")
    return error_response()
```

---

## Performance Impact

### Security Overhead
- Sanitization: < 1ms
- Injection detection: < 5ms
- Off-topic detection: ~0ms (uses existing scores)
- Total overhead: ~5-10ms per request

**Negligible impact on overall pipeline (< 0.5%).**

---

## Security Best Practices

1. **Always validate input**
   - Check for empty queries
   - Sanitize before processing
   - Detect injection attempts

2. **Use allowlists when possible**
   - Define expected query patterns
   - Validate against known good inputs

3. **Log security events**
   - Track injection attempts
   - Monitor off-topic queries
   - Analyze patterns over time

4. **Fail gracefully**
   - Never crash on invalid input
   - Return helpful error messages
   - Maintain conversation_id

5. **Test edge cases**
   - Empty inputs
   - Very long inputs
   - Special characters
   - Unicode
   - Injection attempts

---

## Quick Reference

### SecurityService Methods
```python
# Validation
is_valid, error = validate_query(query)

# Sanitization
sanitized = sanitize_query(query)

# Injection detection
is_injection, pattern = detect_injection_attempt(query)

# Off-topic detection
is_off_topic, score = detect_off_topic(query, passages, scores, threshold)
```

### GenerationService Methods
```python
# Generate with fallback
response = await generate_response(
    query, passages, history, use_fallback_on_error=True
)

# Get fallback message
fallback = get_fallback_response("api_error")
```

### Error Handling Pattern
```python
try:
    # Process query
    result = await process_pipeline(query)
except TimeoutError:
    return timeout_response()
except ValueError:
    return validation_error_response()
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return generic_error_response()
```

---

## File Locations

- **SecurityService**: `backend/src/services/security_service.py`
- **ChatService**: `backend/src/services/chat_service.py`
- **GenerationService**: `backend/src/services/generation_service.py`
- **Tests**: `backend/tests/unit/test_security_service.py`

---

## Support

For questions or issues:
1. Check logs for detailed error messages
2. Review test cases for examples
3. Refer to PHASE4_5_BACKEND_COMPLETION.md for full details
