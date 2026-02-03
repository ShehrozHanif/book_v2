# Backend Quick Start Guide

## Installation

```bash
# Navigate to project directory
cd /c/Users/Shehroz\ Hanif/Desktop/Hackathon1/book

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

## Configuration

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env with your credentials
# Required variables:
# - DATABASE_URL (Neon PostgreSQL)
# - OPENAI_API_KEY
# - QDRANT_URL
# - QDRANT_API_KEY
```

## Database Setup

```bash
# Execute schema against your PostgreSQL database
psql -d your_database < backend/src/database/schema.sql

# Or using pgAdmin/GUI tool, copy contents of schema.sql
```

## Running the Server

```bash
# From project root
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Health Checks

```bash
# Check if API is running
curl http://localhost:8000/health

# Check readiness
curl http://localhost:8000/ready
```

## Making API Calls

### Chat Request Example

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is kinematics?",
    "conversation_id": null,
    "user_id": null
  }'
```

### Expected Response

```json
{
  "response": "RAG pipeline not yet implemented. Please check back soon.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "retrieved_passages": [],
  "relevance_scores": [],
  "processing_time_ms": 2.45
}
```

## File Structure

```
backend/
├── .env                           # Configuration (not in git)
├── .env.example                   # Configuration template
├── requirements.txt               # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration (Pydantic Settings)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.sql             # PostgreSQL schema
│   │   └── connection.py          # Async database connection
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy ORM models
│   │   └── schemas.py             # Pydantic request/response schemas
│   │
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py        # Input validation utilities
│       ├── error_handler.py       # Error handling framework
│       ├── rate_limiter.py        # Rate limiting middleware
│       │
│       └── routes/
│           ├── __init__.py
│           └── chat.py            # Chat API endpoints
│
└── tests/
    ├── unit/                      # Unit tests
    ├── integration/               # Integration tests
    └── contract/                  # Contract tests
```

## API Endpoints

### Health & Info
```
GET /
GET /health
GET /ready
```

### Chat
```
POST /api/v1/chat                          # Send query
POST /api/v1/chat/embed                    # Generate embeddings
GET  /api/v1/chat/conversations/{id}       # Get conversation
DELETE /api/v1/chat/conversations/{id}     # Delete conversation
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=...

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=development

# Rate Limiting (requests per period)
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60

# Query Limits
MAX_QUERY_LENGTH=5000
MIN_QUERY_LENGTH=1

# RAG Settings
TOP_K_RETRIEVAL=5
RELEVANCE_THRESHOLD=0.5

# Session
SESSION_TIMEOUT_HOURS=24
```

## Common Issues

### Issue: `DATABASE_URL environment variable is not set`
**Solution**: Copy `.env.example` to `.env` and fill in the `DATABASE_URL`

### Issue: Connection refused to PostgreSQL
**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct

### Issue: Rate limit exceeded (429)
**Solution**: Default is 10 requests per 60 seconds. Adjust `RATE_LIMIT_REQUESTS` in .env

### Issue: CORS errors from frontend
**Solution**: Update `ALLOWED_ORIGINS` in config.py to include your frontend URL

## Testing

```bash
# Run unit tests
pytest backend/tests/unit/

# Run integration tests
pytest backend/tests/integration/

# Run all tests with coverage
pytest backend/tests/ --cov=backend/src

# Run with verbose output
pytest backend/tests/ -v
```

## Development Tips

### Hot Reload
The `--reload` flag in uvicorn watches for file changes and restarts the server automatically.

### Debug Mode
Set `DEBUG=true` in .env to see more detailed error messages and stack traces.

### Logging
Logs are configured to INFO level. Check the console output when running the server.

### API Documentation
The interactive Swagger UI at `/docs` is useful for testing endpoints:
1. Click "Try it out" on any endpoint
2. Fill in parameters and request body
3. Click "Execute"
4. View response and curl command

## Database Queries

### Check existing tables
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

### View schema
```sql
\d table_name  -- in psql
```

### Check indexes
```sql
SELECT indexname FROM pg_indexes
WHERE tablename = 'conversations';
```

## Performance Monitoring

### Check query time
The `processing_time_ms` field in ChatResponse shows how long each query takes.

### Monitor rate limiter
Rate limiter state is in memory - server restart clears it.

### Database connection pool
NullPool is used for serverless (Neon) - each request gets a new connection.

## Next Steps

1. Implement RAG pipeline in `chat.py` route
2. Add tests in `backend/tests/`
3. Connect Qdrant vector database
4. Integrate OpenAI API
5. Add user authentication
6. Deploy to production environment

## Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Upgrade pip
pip install --upgrade pip

# Check linting
flake8 backend/src

# Format code
black backend/src

# Type checking
mypy backend/src
```

## Support

For issues or questions:
1. Check this quick start guide
2. Review PHASE2_BACKEND_COMPLETION.md for detailed documentation
3. Check error messages in console output
4. Review exception handlers in error_handler.py

## Production Deployment

When deploying to production:

1. Set `ENVIRONMENT=production` in .env
2. Set `DEBUG=false`
3. Update `ALLOWED_ORIGINS` with production domains
4. Use production PostgreSQL database (managed Neon instance)
5. Set proper API keys for OpenAI and Qdrant
6. Configure logging to file instead of console
7. Set up monitoring and alerting
8. Use proper secrets management (not .env file)

---

**Last Updated**: January 30, 2026
**Backend Framework**: FastAPI 0.104.1
**Python Version**: 3.8+
