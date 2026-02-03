# RAG Chatbot Backend - Deployment Guide

FastAPI backend for Humanoid Robotics Textbook RAG Chatbot.

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Qdrant vector database
- OpenAI API key

### 2. Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see below)
```

### 3. Environment Variables

Create `.env` file in `backend/` directory:

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key  # Optional for local

# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot

# Optional: Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

**Required Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and LLM | `sk-...` |
| `QDRANT_URL` | Qdrant vector database URL | `http://localhost:6333` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/db` |

### 4. Database Setup

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=chatbot \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize schema
psql -U user -d chatbot -f src/database/schema.sql
```

### 5. Qdrant Setup

```bash
# Start Qdrant (using Docker)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

### 6. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

API documentation: http://localhost:8000/docs

### 7. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-30T12:34:56Z",
  "version": "1.0.0"
}
```

---

## API Endpoints

### Ask Question

**POST** `/api/v1/chat`

Send a natural language question about the textbook.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "selected_text": "Optional: highlighted text from textbook",
    "conversation_id": "optional-uuid-for-followup"
  }'
```

**Response:**
```json
{
  "response": "ROS 2 is a flexible, open-source middleware framework for robotics development. It provides communication infrastructure, hardware abstraction, and device drivers for building distributed robot applications. [Chapter 1: 1.1 Introduction to ROS 2]",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "retrieved_passages": [
    "ROS 2 is a flexible middleware framework...",
    "It provides communication infrastructure...",
    "Key improvements over ROS 1 include..."
  ],
  "relevance_scores": [0.95, 0.87, 0.86],
  "processing_time_ms": 1234.56
}
```

**Error Responses:**

- `400 Bad Request`: Empty query, invalid input
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Embed Content (Admin)

**POST** `/api/v1/chat/embed`

Embed textbook passages into the vector database.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/embed \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-admin-key" \
  -d '{
    "chunks": [
      {
        "content": "ROS 2 is a flexible middleware framework for building robot applications. It provides communication infrastructure, hardware abstraction, and device drivers.",
        "module": "Module 1: Introduction",
        "chapter": "Chapter 1: ROS Basics",
        "section": "1.1 What is ROS 2?"
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "chunks_embedded": 42,
  "message": "Successfully embedded 42 textbook passages"
}
```

### Health Check

**GET** `/health`

Check service health.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-30T12:34:56Z",
  "version": "1.0.0"
}
```

---

## Architecture

```
backend/
├── src/
│   ├── main.py                  # FastAPI app initialization
│   ├── config.py                # Configuration management
│   ├── logger.py                # Structured logging
│   ├── api/
│   │   ├── routes/
│   │   │   └── chat.py          # Chat endpoints
│   │   ├── dependencies.py      # Validation, rate limiting
│   │   └── error_handler.py     # Error handling middleware
│   ├── services/
│   │   ├── embedding_service.py      # OpenAI embeddings
│   │   ├── retrieval_service.py      # Qdrant vector search
│   │   ├── generation_service.py     # LLM response generation
│   │   ├── chat_service.py           # RAG pipeline orchestration
│   │   ├── conversation_service.py   # Multi-turn context management
│   │   └── security_service.py       # Injection/off-topic detection
│   ├── database/
│   │   ├── connection.py        # Async connection pooling
│   │   └── schema.sql           # PostgreSQL schema
│   └── models/
│       ├── database.py          # SQLAlchemy ORM models
│       └── schemas.py           # Pydantic request/response schemas
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── contract/                # Contract tests
├── contracts/
│   └── openapi.yaml             # OpenAPI 3.0 specification
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
└── pytest.ini                   # Pytest configuration
```

### Service Dependencies

```
ChatService (orchestrator)
├── EmbeddingService → OpenAI API
├── RetrievalService → Qdrant
├── GenerationService → OpenAI API
├── ConversationService → PostgreSQL
└── SecurityService → Validation logic
```

---

## Testing

### Run All Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # On macOS
# or
start htmlcov/index.html  # On Windows
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Contract tests only
pytest tests/contract/ -v

# Run single test file
pytest tests/unit/test_embedding_service.py -v

# Run specific test
pytest tests/unit/test_chat_service.py::test_process_query -v
```

### Test Coverage Goals

- Overall: > 80%
- Services: > 90%
- API routes: > 85%

---

## Performance SLAs

### Latency Targets (p95)

| Operation | Target | Notes |
|-----------|--------|-------|
| **Total Response** | < 3s | End-to-end query processing |
| Embedding API | < 500ms | OpenAI `text-embedding-3-small` |
| Qdrant Search | < 1s | Vector similarity search |
| LLM Generation | < 2.5s | OpenAI GPT-4o-mini |
| Database Save | < 100ms | PostgreSQL insert |

### Retrieval Quality

- **Relevance Score**: > 0.85 average
- **Passages Retrieved**: 3-5 per query
- **Citation Accuracy**: > 95%

### API Cost Monitoring

Each request logs:
- Embedding tokens (OpenAI)
- LLM tokens (OpenAI)
- Estimated cost

View daily costs:
```bash
# Aggregate from logs
grep "cost=" logs/app.log | awk -F'cost=\\$' '{sum+=$2} END {print "Total: $" sum}'
```

---

## Logging and Monitoring

### Structured Logging

All operations log structured JSON:

```json
{
  "timestamp": "2024-01-30T12:34:56Z",
  "level": "INFO",
  "message": "Query processed",
  "conv_id": "550e8400...",
  "processing_time_ms": 1234,
  "num_passages": 3,
  "avg_relevance": 0.89
}
```

### Log Files

- **Location**: `logs/app.log`
- **Rotation**: Daily
- **Retention**: 30 days

### View Logs

```bash
# Tail logs in real-time
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log | jq .

# View performance metrics
grep "Performance:" logs/app.log
```

### Metrics to Monitor

1. **Latency**: p50, p95, p99 response times
2. **Error Rate**: 5xx errors / total requests
3. **API Costs**: Daily OpenAI spending
4. **Retrieval Quality**: Average relevance scores
5. **Database Performance**: Query execution time

---

## Deployment

### Docker Deployment

#### Build Image

```bash
cd backend

docker build -t rag-chatbot:latest .
```

#### Run Container

```bash
docker run -d \
  --name rag-chatbot \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e DATABASE_URL=postgresql://... \
  -e QDRANT_URL=http://qdrant:6333 \
  rag-chatbot:latest
```

#### Docker Compose (Full Stack)

See root `docker-compose.yml` for full stack deployment.

```bash
# Start all services (backend, frontend, PostgreSQL, Qdrant)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Production Deployment

#### Recommended Setup

- **Compute**: 2 vCPU, 4GB RAM
- **Database**: PostgreSQL managed service (AWS RDS, Neon, etc.)
- **Vector DB**: Qdrant Cloud or self-hosted
- **Reverse Proxy**: Nginx with SSL/TLS

#### Environment Variables (Production)

```env
# Production settings
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.example.com/chatbot
QDRANT_URL=https://qdrant.example.com:6333
QDRANT_API_KEY=prod-api-key
OPENAI_API_KEY=sk-prod-...

# Optional: Monitoring
SENTRY_DSN=https://...  # Error tracking
```

#### Health Checks

Configure health check endpoint:

- **URL**: `GET /health`
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3

---

## Troubleshooting

### "Connection refused" errors

**Cause**: PostgreSQL not running or wrong credentials

**Solution**:
```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### "Invalid API key" from OpenAI

**Cause**: Missing or invalid OpenAI API key

**Solution**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check permissions (needs embeddings + chat)
```

### "No vector results" from Qdrant

**Cause**: Empty vector database

**Solution**:
```bash
# Embed textbook content first
curl -X POST http://localhost:8000/api/v1/chat/embed \
  -H "Content-Type: application/json" \
  -d '{
    "chunks": [
      {
        "content": "Your textbook passage here...",
        "module": "Module 1",
        "chapter": "Chapter 1",
        "section": "1.1"
      }
    ]
  }'

# Verify embeddings in Qdrant
curl http://localhost:6333/collections/textbook_chunks
```

### High latency (> 5s)

**Possible causes**:
- OpenAI API throttling
- Large conversation history
- Slow database queries

**Solutions**:
```bash
# Check OpenAI rate limits
grep "Embedding API" logs/app.log | tail -20

# Monitor database performance
grep "Database" logs/app.log

# Reduce conversation context
# Edit config.py: MAX_CONTEXT_MESSAGES = 10
```

### Memory leaks

**Cause**: Async sessions not closed properly

**Solution**:
```bash
# Monitor memory usage
docker stats rag-chatbot

# Check for unclosed sessions (in logs)
grep "Session" logs/app.log

# Restart service
docker restart rag-chatbot
```

---

## Cost Monitoring

### OpenAI API Costs

**Embedding Model** (`text-embedding-3-small`):
- Cost: $0.00002 / 1K tokens
- Average query: ~50 tokens = $0.000001

**LLM Model** (`gpt-4o-mini`):
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Average query: ~1000 input + 200 output = $0.00027

**Daily Cost Estimate** (1000 queries/day):
- Embeddings: $0.001
- LLM: $0.27
- **Total**: ~$0.27/day (~$8/month)

### View Costs from Logs

```bash
# Today's embedding costs
grep "Embedding API" logs/app.log | \
  awk -F'cost=\\$' '{sum+=$2} END {print "Embeddings: $" sum}'

# Today's generation costs
grep "Generation API" logs/app.log | \
  awk -F'cost=\\$' '{sum+=$2} END {print "Generation: $" sum}'
```

---

## Security

### API Key Protection

- Store in `.env` (never commit)
- Use secrets management in production (AWS Secrets Manager, etc.)
- Rotate keys quarterly

### Rate Limiting

- Default: 60 requests/minute per IP
- Configured in `src/api/dependencies.py`

### Input Validation

- Max query length: 5000 characters
- Injection detection enabled
- Off-topic detection enabled

### Database Security

- Use strong passwords
- Enable SSL for database connections
- Restrict network access

---

## Contributing

### Development Workflow

1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Ensure coverage > 80%
5. Run linters: `black src/` and `pylint src/`
6. Submit pull request

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
pylint src/

# Type check
mypy src/
```

---

## Support

- **Documentation**: `/docs` (Swagger UI)
- **OpenAPI Spec**: `contracts/openapi.yaml`
- **Issues**: GitHub Issues
- **Email**: support@roboticsbook.ai

---

**Last Updated**: 2024-01-30

**Version**: 1.0.0
