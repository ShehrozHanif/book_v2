# RAG Pipeline Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React/Next.js)                        │
│                        Student Asks: "What is ROS 2?"                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI HTTP Server                                │
│                     POST /api/v1/chat (T028 Endpoint)                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Rate Limiter: Check 10 req/min per IP                             │  │
│  │ 2. Request Validator: Check query length, SQL injection, UUIDs       │  │
│  │ 3. Create ChatService instance                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Chat Orchestration Service (T027)                       │
│                   Coordinates the RAG Pipeline Steps                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Step 1: Embed Query                                                    │  │
│  │ Step 2: Retrieve Passages                                              │  │
│  │ Step 3: Load Conversation History                                      │  │
│  │ Step 4: Generate Response                                              │  │
│  │ Step 5: Save Messages to Database                                      │  │
│  │ Step 6: Return ChatResponse                                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  Embedding       │ │  Conversation    │ │  Retrieval       │
        │  Service (T024)  │ │  Service (DB)    │ │  Service (T025)  │
        │                  │ │                  │ │                  │
        │ embed_query()    │ │ load_conversation│ │ retrieve_context │
        │     ↓            │ │        ↓         │ │      ↓           │
        │ OpenAI API       │ │    PostgreSQL    │ │ Qdrant Vector DB │
        │     ↓            │ │                  │ │      ↓           │
        │1536-dim vector   │ │ History msgs     │ │ Top 3 passages   │
        └──────────────────┘ │ + relevance      │ │ + scores         │
                             │  scores          │ └──────────────────┘
                             └──────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
        ┌──────────────────────────────┐    ┌──────────────────────────┐
        │  Generation Service (T026)   │    │  Database (Messages)     │
        │                              │    │                          │
        │  generate_response()         │    │  Save:                   │
        │      ↓                       │    │  - User query            │
        │  OpenAI GPT API              │    │  - Bot response          │
        │      ↓                       │    │  - Conversation ID       │
        │  "ROS 2 is a robotics..."   │    │  - Timestamps            │
        │  [Chapter 1: Fundamentals]   │    │                          │
        │      ↓                       │    │                          │
        │  extract_citations()         │    └──────────────────────────┘
        │  validate_response()         │
        └──────────────────────────────┘
                    │
                    └─────────────────────────────────┬─────────────────────────┐
                                                      │                         │
                                                      ▼                         ▼
                                        ┌─────────────────────┐  ┌──────────────────────┐
                                        │  ChatResponse       │  │  HTTP 200            │
                                        │                     │  │  Response Headers:   │
                                        │  {                  │  │  - X-RateLimit-*     │
                                        │    "response": "...",│  │  - Content-Type      │
                                        │    "passages": [...],│  │  - Cache-Control     │
                                        │    "scores": [...],  │  │                      │
                                        │    "timing_ms": ...  │  │  Return to Frontend  │
                                        │  }                  │  │                      │
                                        └─────────────────────┘  └──────────────────────┘
                                                      │
                                                      ▼
                        ┌─────────────────────────────────────────────────────┐
                        │            Frontend (React/Next.js)                 │
                        │                                                     │
                        │  Display:                                           │
                        │  - Response text with citations highlighted        │
                        │  - Retrieved passages                              │
                        │  - Relevance scores                                │
                        │  - Processing time                                 │
                        │  - Continue conversation                           │
                        └─────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Request to Response Flow

```
CLIENT REQUEST
    │
    └─► POST /api/v1/chat
        {
          "query": "What is ROS 2?",
          "conversation_id": "uuid-123"
        }
        │
        ▼
RATE LIMITING CHECK
    ├─ Get client IP
    ├─ Check request count
    └─ If exceeded: return 429 Too Many Requests
        │
        ▼ (if allowed)
REQUEST VALIDATION
    ├─ Validate query length (1-5000 chars)
    ├─ Validate UUIDs format
    ├─ Detect SQL injection patterns
    └─ If invalid: return 400 Bad Request
        │
        ▼ (if valid)
PIPELINE EXECUTION
    │
    ├─► [1] EMBEDDING SERVICE
    │   ├─ Input: "What is ROS 2?" (string)
    │   ├─ OpenAI embed_text() API call
    │   └─ Output: [0.001, 0.002, ..., 0.003] (1536 floats)
    │
    ├─► [2] RETRIEVAL SERVICE
    │   ├─ Input: [0.001, 0.002, ..., 0.003] (1536 dims)
    │   ├─ Qdrant search(vector, top_k=5)
    │   ├─ Filter by min_relevance (0.3)
    │   ├─ Rank by score descending
    │   └─ Output:
    │       passages = ["ROS 2 is...", "ROS 2 uses...", ...]
    │       scores = [0.95, 0.87, 0.82]
    │
    ├─► [3] CONVERSATION HISTORY (if multi-turn)
    │   ├─ Query database for conversation_id
    │   ├─ Load last 20 messages (max 2000 tokens)
    │   └─ Format for LLM: [{"role": "user", ...}, ...]
    │
    ├─► [4] GENERATION SERVICE
    │   ├─ Input:
    │   │   - query: "What is ROS 2?"
    │   │   - passages: ["ROS 2 is...", ...]
    │   │   - history: [{"role": "user", ...}, ...]
    │   ├─ OpenAI chat.completions() API call
    │   │   system: "You are an educational assistant..."
    │   │   user: "[PASSAGE]ROS 2 is...[/PASSAGE]... Question: What is ROS 2?"
    │   │   history: [previous messages]
    │   │   max_tokens: 500
    │   ├─ Output: "ROS 2 is a robotics framework. [Chapter 1: Fundamentals]"
    │   ├─ extract_citations()
    │   └─ validate_response()
    │
    └─► [5] MESSAGE PERSISTENCE
        ├─ Save: Message(conversation_id, sender="user", content="What is ROS 2?")
        ├─ Save: Message(conversation_id, sender="assistant", content="ROS 2 is...")
        └─ Database commit

RESPONSE CONSTRUCTION
    │
    ├─ Measure total processing time
    ├─ Construct ChatResponse JSON
    └─ Add rate limit headers

RESPONSE SENT TO CLIENT
    │
    └─► HTTP 200 OK
        {
          "response": "ROS 2 is a robotics...[Chapter 1: Fundamentals]",
          "conversation_id": "uuid-123",
          "retrieved_passages": ["ROS 2 is...", "ROS 2 uses...", ...],
          "relevance_scores": [0.95, 0.87, 0.82],
          "processing_time_ms": 1245.5
        }

        Headers:
        X-RateLimit-Limit: 10
        X-RateLimit-Remaining: 9
        X-RateLimit-Reset: 1704067260
```

---

## Service Interaction Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         ChatService (T027 Orchestrator)                    │
│                                                                            │
│  process_query(query, conversation_id, user_id) → ChatResponse           │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  PIPELINE EXECUTION STEPS                                          │  │
│  │                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │ 1. await embedding_service.embed_query(query)              │  │  │
│  │  │    Returns: List[float] (1536 dims)                         │  │  │
│  │  └──────────────────────────┬──────────────────────────────────┘  │  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │ 2. await retrieval_service.retrieve_context(vector, query)  │  │  │
│  │  │    Returns: (passages: List[str], scores: List[float])     │  │  │
│  │  └──────────────────────────┬──────────────────────────────────┘  │  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │ 3. conversation_service = await get_conversation_service()  │  │  │
│  │  │    history = await conv_service.load_conversation()         │  │  │
│  │  │    Returns: List[Dict] (formatted for LLM)                 │  │  │
│  │  └──────────────────────────┬──────────────────────────────────┘  │  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │ 4. await generation_service.generate_response()             │  │  │
│  │  │    (query, passages, history)                              │  │  │
│  │  │    Returns: str (response with citations)                  │  │  │
│  │  └──────────────────────────┬──────────────────────────────────┘  │  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │ 5. await conversation_service.save_message()                │  │  │
│  │  │    - Save user query                                        │  │  │
│  │  │    - Save bot response                                      │  │  │
│  │  │    - Commit to database                                     │  │  │
│  │  └──────────────────────────┬──────────────────────────────────┘  │  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │ 6. Return ChatResponse                                       │  │  │
│  │  │    {                                                         │  │  │
│  │  │      response: str,                                         │  │  │
│  │  │      conversation_id: str,                                  │  │  │
│  │  │      retrieved_passages: List[str],                         │  │  │
│  │  │      relevance_scores: List[float],                         │  │  │
│  │  │      processing_time_ms: float                              │  │  │
│  │  │    }                                                         │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  DEPENDENCIES (Injected):                                                │
│  ├─ embedding_service: EmbeddingService                                 │
│  ├─ retrieval_service: RetrievalService                                 │
│  ├─ generation_service: GenerationService                               │
│  └─ session: AsyncSession (for conversation_service)                    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## External Service Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAG Pipeline Services                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EmbeddingService ◄──────────► OpenAI Embeddings API                       │
│  (T024)                        text-embedding-3-small                      │
│                                Returns: 1536-dim vectors                   │
│                                Latency: ~100ms                             │
│                                                                             │
│  RetrievalService ◄──────────► Qdrant Vector Database                      │
│  (T025)                        (Cloud or Self-hosted)                      │
│                                Collection: textbook_chunks                 │
│                                Distance: COSINE                            │
│                                Latency: ~50ms                              │
│                                                                             │
│  GenerationService ◄──────────► OpenAI Chat Completions API               │
│  (T026)                        Model: gpt-3.5-turbo (or gpt-4)            │
│                                Returns: Generated text                     │
│                                Latency: ~900ms                             │
│                                                                             │
│  ConversationService ◄──────────► PostgreSQL Database                      │
│  (Existing)                     Tables:                                    │
│                                  - conversations                           │
│                                  - messages                                │
│                                  - users                                   │
│                                Latency: ~50ms                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
ChatService.process_query()
    │
    ├─ Exception during embed_query()
    │   └─► Log error → Re-raise → HTTP 500
    │
    ├─ Exception during retrieve_context()
    │   └─► Log error → Re-raise → HTTP 500
    │
    ├─ Exception during load_conversation()
    │   └─► Log warning → Continue without history (graceful degradation)
    │
    ├─ Exception during generate_response()
    │   └─► Log error → Re-raise → HTTP 500
    │
    ├─ Exception during save_message()
    │   └─► Log error → Rollback database → Continue (non-blocking)
    │
    └─ Success
        └─► Return ChatResponse with all metadata

/chat Endpoint Error Handling
    │
    ├─ HTTP 400 Bad Request
    │   ├─ Query length validation fails
    │   ├─ UUID format invalid
    │   ├─ SQL injection patterns detected
    │   └─ Return: {"detail": "error message"}
    │
    ├─ HTTP 429 Too Many Requests
    │   ├─ Rate limit exceeded (>10 req/min per IP)
    │   └─ Headers: X-RateLimit-* status
    │
    ├─ HTTP 500 Internal Server Error
    │   ├─ Any unhandled exception in pipeline
    │   ├─ Database connection failed
    │   ├─ External API unavailable
    │   └─ Return: {"detail": "Failed to process chat request"}
    │
    └─ HTTP 200 OK
        └─ Return ChatResponse with all metadata
```

---

## Performance and Scalability

### Response Time Breakdown
```
Request Validation:     ~5ms
Query Embedding:        ~100ms   (OpenAI API)
Vector Search:          ~50ms    (Qdrant)
Load Conversation:      ~30ms    (Database)
Response Generation:    ~900ms   (OpenAI API)
Message Storage:        ~50ms    (Database)
Response Serialization: ~10ms    (JSON)
─────────────────────────────────
TOTAL:                  ~1145ms  (Target: <3000ms) ✓
```

### Scalability Metrics
```
Rate Limiting:          10 req/min per IP
Estimated Max Users:    ~100 concurrent (10 req/min each)
Message Context Window: 2000 tokens max (20 messages)
Context Passages:       3 passages (customizable)
Conversation History:   Last 20 messages (configurable)
```

### Resource Usage
```
Memory per Request:
  - Query vector:       6 KB (1536 floats × 4 bytes)
  - Context passages:   1.5 KB (3 passages × 500 chars avg)
  - Response:           2 KB (500 chars avg)
  - Conversation cache: Variable (up to 2000 tokens)
  ─────────────────────
  TOTAL:                ~20 KB per concurrent request

Database Connections:   1 async session per request
Vector DB Connections:  1 connection pool (shared)
OpenAI Connections:     1 async client (shared)
```
