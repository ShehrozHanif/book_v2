# RAG Chatbot Backend

FastAPI-based backend for the RAG Chatbot application.

## Project Structure

```
src/
├── api/              # API routes and dependencies
├── models/           # Data models and schemas
├── services/         # Business logic
├── database/         # Database configuration
├── config.py         # Application configuration
└── main.py           # FastAPI application entry point

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── contract/         # Contract/API tests
```

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Run the application:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

Run tests with:
```bash
pytest tests/
```

## Docker

Build and run with Docker:
```bash
docker build -t rag-chatbot-backend .
docker run -p 8000:8000 rag-chatbot-backend
```
