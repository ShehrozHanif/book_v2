# RAG (Retrieval-Augmented Generation) Pipeline Implementation

This document describes the complete RAG pipeline implementation for User Story 1 MVP, which powers the AI chatbot with context-aware responses based on textbook content.

## Architecture Overview

The RAG pipeline consists of 5 main services working together:

```
User Query
    ↓
[T024] Embedding Service
    - Query → 1536-dim vector
    ↓
[T025] Retrieval Service
    - Vector → Qdrant search → top-5 passages
    - Filter by relevance threshold
    - Rank by score
    - Select top-3 for context
    ↓
[T026] Generation Service
    - Query + context + history → LLM
    - Extract citations [Chapter X: Section Y]
    - Validate response (no hallucinations)
    ↓
[T027] Chat Orchestration
    - Coordinate all steps
    - Load conversation history
    - Save messages to database
    - Return ChatResponse
    ↓
[T028] /chat Endpoint
    - HTTP POST handler
    - Request validation
    - Rate limiting
    - Response formatting
    ↓
HTTP 200 Response
{
    "response": "ROS 2 is...",
    "retrieved_passages": [...],
    "relevance_scores": [...],
    "processing_time_ms": 1250
}
```

## Service Implementation Details

### T024: Embedding Service (`backend/src/services/embedding_service.py`)

**Purpose**: Convert text (queries and passages) into vector embeddings for semantic search.

**Key Methods**:
- `embed_query(query: str) → List[float]`: Embed single query
  - Returns 1536-dimensional OpenAI embedding vector
  - Used for vector search in Qdrant

- `embed_passages(passages: List[dict]) → List[dict]`: Batch embed passages
  - Takes list of passage dictionaries with 'content' field
  - Returns passages with added 'vector' and 'id' fields
  - Preserves all original metadata (module, chapter, section, etc.)

**Technical Details**:
- Uses OpenAI's `text-embedding-3-small` model (1536 dimensions)
- Async/await for non-blocking execution
- Error handling with logging
- Singleton pattern for service instance

**Example**:
```python
from src.services.embedding_service import get_embedding_service

embedding_service = get_embedding_service()
query_vector = await embedding_service.embed_query("What is ROS 2?")
# → [0.001, 0.002, ..., 0.003]  # 1536 floats
```

### T025: Retrieval Service (`backend/src/services/retrieval_service.py`)

**Purpose**: Find relevant textbook passages using vector similarity search.

**Key Methods**:
- `search(query_vector: List[float]) → List[Dict]`: Vector similarity search
  - Queries Qdrant vector database
  - Returns top-5 most similar passages
  - Each result includes score, id, and payload (content + metadata)

- `rank_passages(passages, query) → List[Dict]`: Filter and rank results
  - Filters passages by minimum relevance threshold (0.3 default)
  - Sorts by relevance score descending

- `retrieve_context(query_vector, query, top_k=3) → (passages, scores)`: Full pipeline
  - Performs search + ranking
  - Returns top-3 passages + scores for LLM context window
  - Tuple of (passage_texts: List[str], scores: List[float])

**Technical Details**:
- Uses Qdrant Cloud for vector similarity search
- COSINE distance metric
- Configurable top_k (default: 5 from Qdrant)
- Configurable min_relevance (default: 0.3)
- Returns top-3 for LLM context (default)

**Example**:
```python
from src.services.retrieval_service import get_retrieval_service

retrieval_service = get_retrieval_service()
passages, scores = await retrieval_service.retrieve_context(
    query_vector=[0.1, 0.2, ...],  # 1536 dims
    query="What is kinematics?",
    top_k=3
)
# → (
#     ["Kinematics is the study of motion", ...],
#     [0.95, 0.87, 0.82]
#   )
```

### T026: Generation Service (`backend/src/services/generation_service.py`)

**Purpose**: Generate contextual responses using OpenAI GPT with textbook passages as context.

**Key Methods**:
- `generate_response(query, context_passages, conversation_history) → str`: Generate LLM response
  - Calls OpenAI chat completions API
  - Includes system prompt for educational context
  - Supports multi-turn conversations
  - Max tokens: 500 (configurable)

- `extract_citations(response) → List[str]`: Extract citations from response
  - Finds patterns like [Chapter 1: Fundamentals]
  - Regex: `\[(?:Chapter|Module)\s+\d+(?::\s*[^\]]+)?\]`

- `validate_response(response, context_passages) → bool`: Check response grounding
  - Checks for citations
  - Logs warnings for potentially ungrounded responses
  - Currently allows all responses but logs for monitoring

**Technical Details**:
- Uses OpenAI GPT-3.5-turbo or configurable model
- System prompt instructs to use only provided context
- Formats context passages for inclusion in prompt
- Supports conversation history for multi-turn chats
- Async/await for non-blocking execution

**Example**:
```python
from src.services.generation_service import get_generation_service

generation_service = get_generation_service()
response = await generation_service.generate_response(
    query="What is ROS 2?",
    context_passages=[
        "ROS 2 is a robotics middleware framework...",
        "It provides communication patterns..."
    ],
    conversation_history=[
        {"role": "user", "content": "What is robotics?"},
        {"role": "assistant", "content": "Robotics is the field of..."}
    ]
)
# → "ROS 2 is a robotics middleware framework. [Chapter 1: Fundamentals]"
```

### T027: Chat Orchestration Service (`backend/src/services/chat_service.py`)

**Purpose**: Orchestrate the full RAG pipeline and manage conversation state.

**Key Methods**:
- `process_query(query, conversation_id, user_id) → ChatResponse`: Process query through pipeline

  Pipeline steps:
  1. Embed query (T024)
  2. Retrieve passages (T025)
  3. Load conversation history
  4. Generate response (T026)
  5. Save messages to database
  6. Return ChatResponse

**Technical Details**:
- Coordinates embedding → retrieval → generation pipeline
- Loads conversation history from database
- Saves user query and bot response
- Measures total processing time
- Error handling with automatic rollback on database errors
- Handles invalid UUIDs gracefully

**Example**:
```python
from src.services.chat_service import get_chat_service

chat_service = await get_chat_service(db_session)
response = await chat_service.process_query(
    query="What is humanoid robotics?",
    conversation_id="550e8400-e29b-41d4-a716-446655440000",
    user_id="user-123"
)
# → ChatResponse(
#     response="Humanoid robotics is...",
#     conversation_id="550e8400-e29b-41d4-a716-446655440000",
#     retrieved_passages=[...],
#     relevance_scores=[0.95, 0.87, 0.82],
#     processing_time_ms=1245.5
#   )
```

### T028: /chat Endpoint (`backend/src/api/routes/chat.py`)

**Purpose**: HTTP endpoint for frontend to send queries to RAG chatbot.

**Endpoint**:
- **Path**: `POST /api/v1/chat`
- **Rate Limit**: 10 requests per minute per IP
- **Status Codes**: 200 (OK), 400 (validation error), 429 (rate limit), 500 (server error)

**Request Schema** (`ChatRequest`):
```json
{
    "query": "What is ROS 2?",              // Required: 1-5000 chars
    "selected_text": null,                  // Optional: highlighted text
    "conversation_id": "uuid-string",       // Optional: for multi-turn
    "user_id": "uuid-string"                // Optional: user tracking
}
```

**Response Schema** (`ChatResponse`):
```json
{
    "response": "ROS 2 is a robotics middleware...[Chapter 1: Fundamentals]",
    "conversation_id": "uuid-string",
    "retrieved_passages": [
        "ROS 2 is a robotics middleware framework...",
        "It provides publish-subscribe communication...",
        "ROS 2 supports real-time applications..."
    ],
    "relevance_scores": [0.95, 0.87, 0.82],
    "processing_time_ms": 1245.5
}
```

**Validation**:
- Query must be 1-5000 characters
- Conversation ID and user ID must be valid UUIDs (if provided)
- SQL injection patterns are detected and rejected
- Selected text limited to 2000 characters

**Error Responses**:
```json
// 400 Bad Request
{
    "detail": "Query must be between 1 and 5000 characters"
}

// 500 Internal Server Error
{
    "detail": "Failed to process chat request"
}
```

**Rate Limiting Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1704067260
```

## Full Pipeline Flow: Step-by-Step

### Example: Student asks about ROS 2

1. **Frontend** (React/Next.js)
   - Student types "What is ROS 2?" in chat input
   - Clicks "Send" button
   - Frontend calls: `POST /api/v1/chat` with JSON:
   ```json
   {
       "query": "What is ROS 2?",
       "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
   }
   ```

2. **T028: /chat Endpoint**
   - Receives request
   - Rate limiter checks IP: 9/10 requests remaining
   - Calls `validate_chat_request()`: validates query, UUID format
   - Creates ChatService instance
   - Calls `chat_service.process_query()`

3. **T027: Chat Service**
   - Starts timer
   - Validates conversation_id is valid UUID
   - Proceeds with pipeline

4. **T024: Embedding Service**
   - Calls OpenAI API: `embed_text("What is ROS 2?")`
   - Gets 1536-dimensional vector
   - Returns: `[0.001, 0.002, ..., 0.003]`

5. **T025: Retrieval Service**
   - Calls Qdrant: `search([0.001, 0.002, ...], top_k=5)`
   - Qdrant returns top-5 similar passages:
   ```
   [
       {id: "chunk_123", score: 0.95, content: "ROS 2 is a robotics..."},
       {id: "chunk_456", score: 0.87, content: "ROS 2 uses publish-subscribe..."},
       {id: "chunk_789", score: 0.82, content: "ROS 2 supports real-time..."},
       {id: "chunk_012", score: 0.76, content: "ROS 2 middleware provides..."},
       {id: "chunk_345", score: 0.65, content: "ROS 2 is compatible with..."}
   ]
   ```
   - Ranks and filters by min_relevance (0.3): all 5 pass
   - Returns top-3 for context:
   ```
   passages = [
       "ROS 2 is a robotics...",
       "ROS 2 uses publish-subscribe...",
       "ROS 2 supports real-time..."
   ]
   scores = [0.95, 0.87, 0.82]
   ```

6. **Load Conversation History**
   - Gets previous messages from database (if multi-turn):
   ```
   [
       {"role": "user", "content": "What is robotics?"},
       {"role": "assistant", "content": "Robotics is the field of..."}
   ]
   ```

7. **T026: Generation Service**
   - Calls OpenAI Chat Completions API with:
   ```
   system: "You are a helpful educational assistant for a Humanoid Robotics textbook..."
   user: "Provided passages:\n[PASSAGE]\nROS 2 is a robotics...\n[/PASSAGE]\n\n[PASSAGE]\nROS 2 uses...\n[/PASSAGE]\n\nQuestion: What is ROS 2?"
   conversation_history: [...]
   max_tokens: 500
   ```
   - OpenAI returns:
   ```
   "ROS 2 is a robotics middleware framework for building distributed robot applications. [Chapter 1: Fundamentals] It provides a communication system that allows different parts of a robot system to exchange data through publish-subscribe patterns. [Chapter 2: Architecture] ROS 2 also supports real-time applications and is compatible with multiple operating systems."
   ```
   - Extracts citations: `["[Chapter 1: Fundamentals]", "[Chapter 2: Architecture]"]`
   - Validates response: passes (has citations)

8. **Save to Database**
   - Creates message: `Message(sender="user", content="What is ROS 2?")`
   - Creates message: `Message(sender="assistant", content="ROS 2 is a robotics...")`
   - Saves both to database with conversation_id

9. **Return Response**
   - Constructs ChatResponse:
   ```json
   {
       "response": "ROS 2 is a robotics middleware...[Chapter 1: Fundamentals]",
       "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
       "retrieved_passages": [
           "ROS 2 is a robotics...",
           "ROS 2 uses publish-subscribe...",
           "ROS 2 supports real-time..."
       ],
       "relevance_scores": [0.95, 0.87, 0.82],
       "processing_time_ms": 1245.5
   }
   ```
   - Returns 200 with response (includes rate limit headers)

10. **Frontend**
    - Receives response
    - Displays bot message with citations highlighted
    - Shows relevance scores on hover over passages
    - Updates conversation history

**Total Latency**: 1.25 seconds (meeting <3s requirement)

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4

# Qdrant Vector Database
QDRANT_URL=https://xxxxx-xxx-xxxxx.qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=textbook_chunks

# RAG Configuration
TOP_K_RETRIEVAL=5            # Top K from Qdrant
RELEVANCE_THRESHOLD=0.5      # Min relevance score

# Rate Limiting
RATE_LIMIT_REQUESTS=10       # Per IP
RATE_LIMIT_PERIOD=60         # Seconds

# Query Limits
MAX_QUERY_LENGTH=5000
MIN_QUERY_LENGTH=1
```

## Testing

### Unit Tests

Test each service independently:

```bash
# Embedding service tests
pytest backend/tests/unit/test_embedding_service.py -v

# Retrieval service tests
pytest backend/tests/unit/test_retrieval_service.py -v

# Generation service tests
pytest backend/tests/unit/test_generation_service.py -v
```

### Integration Tests

Test full RAG pipeline:

```bash
# Full pipeline tests
pytest backend/tests/integration/test_chat_pipeline.py -v
```

### Manual Testing

Using curl:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

## Performance Metrics

**Expected Latencies** (per SC-001):
- Query embedding: ~100ms
- Vector search (Qdrant): ~50ms
- LLM generation: ~900ms
- Database save: ~50ms
- **Total: ~1.1 seconds** (target <3 seconds) ✓

**Memory Usage**:
- Embedding vectors: 1536 floats × 4 bytes = 6KB per query
- Retrieval results: 3 passages × 500 chars avg = 1.5KB
- Conversation history: varies, capped at 2000 tokens

**Throughput**:
- 10 requests/minute per IP (rate limiting)
- Can handle ~100 concurrent users (with 10 req/min each)

## Error Handling

### Validation Errors (400)
- Query too short or too long
- Invalid UUID format
- SQL injection patterns detected

### Server Errors (500)
- OpenAI API unavailable
- Qdrant connection failed
- Database operation failed
- Message saving failed (non-blocking, continues)

### Rate Limiting (429)
- IP exceeds 10 requests/minute

## Future Enhancements

1. **Passage Metadata Filtering**: Filter by chapter/module
2. **Conversation Summarization**: Create conversation summaries for context
3. **Citation Highlighting**: Highlight exact passages cited
4. **Feedback Loop**: Track user satisfaction with responses
5. **Fine-tuning**: Fine-tune models on textbook domain
6. **Caching**: Cache frequent queries and responses
7. **Streaming**: Stream responses for faster perceived latency
8. **Multi-language**: Support multiple languages

## Monitoring and Logging

### Key Metrics to Monitor

- Query embedding latency
- Vector search latency (Qdrant)
- LLM generation latency
- End-to-end latency
- Rate limit hit rate
- Error rate by type
- Retrieved passage relevance scores

### Log Levels

- **DEBUG**: Detailed pipeline steps, cache hits
- **INFO**: Queries processed, pipeline timing, messages saved
- **WARNING**: Low relevance scores, missing citations, conversation loading failed
- **ERROR**: API failures, validation failures, database errors

### Example Logs

```
INFO: Embedded query: 42 chars → 1536 dims
INFO: Qdrant search returned 5 results
INFO: Ranked 5 passages → 5 relevant (threshold: 0.3)
INFO: Retrieved 3 passages for context
INFO: Generated response (245 chars, valid=True)
INFO: Query processed in 1245.0ms (embedding, retrieval, generation, storage)
```
