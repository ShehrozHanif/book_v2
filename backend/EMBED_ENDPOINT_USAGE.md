# Content Embedding Endpoint Usage Guide

## Overview

The `/api/v1/chat/embed` endpoint is an admin endpoint for embedding and indexing textbook content into Qdrant vector database for RAG (Retrieval-Augmented Generation) retrieval.

## Endpoint Details

**URL**: `POST /api/v1/chat/embed`

**Purpose**: Embed textbook passages and store them in Qdrant for semantic search during chat retrieval

## Request Format

### Request Body Schema

```json
{
  "chunks": [
    {
      "content": "string (10-5000 chars)",
      "module": "string (1-100 chars)",
      "chapter": "string (1-200 chars)",
      "section": "string (1-200 chars)"
    }
  ],
  "collection_name": "string (optional, default: 'textbook_chunks')"
}
```

### Parameters

- **chunks** (required, array): List of textbook chunks to embed
  - **content** (required, string): The actual paragraph/section text (recommended 200-500 words)
  - **module** (required, string): Module identifier (e.g., "Module 1: ROS 2 Basics")
  - **chapter** (required, string): Chapter identifier (e.g., "Chapter 1: Fundamentals")
  - **section** (required, string): Section identifier (e.g., "1.1 Introduction to ROS 2")

- **collection_name** (optional, string): Qdrant collection name for storage (default: "textbook_chunks")

## Response Format

### Success Response (HTTP 200)

```json
{
  "success": true,
  "chunks_embedded": 5,
  "collection": "textbook_chunks",
  "message": "Successfully embedded 5 passages into 'textbook_chunks' in 2.45s"
}
```

### Response Fields

- **success** (boolean): Whether embedding succeeded
- **chunks_embedded** (integer): Number of chunks successfully embedded and indexed
- **collection** (string): Qdrant collection name used for storage
- **message** (string): Status message with processing details

## Error Responses

### 400 Bad Request

Empty chunks list or validation failure:

```json
{
  "error": "Invalid request",
  "details": "No chunks provided",
  "status_code": 400
}
```

### 422 Unprocessable Entity

Invalid chunk format (missing fields, content too short/long):

```json
{
  "detail": [
    {
      "loc": ["body", "chunks", 0, "content"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.string.too_short"
    }
  ]
}
```

### 500 Internal Server Error

Embedding or Qdrant indexing failed:

```json
{
  "error": "Embedding pipeline failed",
  "details": "Failed to embed passages: OpenAI API error",
  "status_code": 500
}
```

## Example Usage

### Basic cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/chat/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "chunks": [
      {
        "content": "ROS 2 (Robot Operating System 2) is a flexible middleware for writing robot software. It is a collection of tools and libraries that help you build robot applications across a wide variety of robotic platforms.",
        "module": "Module 1",
        "chapter": "Chapter 1: Fundamentals",
        "section": "1.1 Introduction to ROS 2"
      },
      {
        "content": "The core concept in ROS 2 is the ability to design complex robot software systems by composing reusable software components. ROS 2 promotes the development of robust and modular robot software.",
        "module": "Module 1",
        "chapter": "Chapter 1: Fundamentals",
        "section": "1.2 Core Concepts"
      }
    ],
    "collection_name": "textbook_chunks"
  }'
```

### Python Example Using Requests

```python
import requests

url = "http://localhost:8000/api/v1/chat/embed"

payload = {
    "chunks": [
        {
            "content": "ROS 2 is a flexible middleware for robot software...",
            "module": "Module 1",
            "chapter": "Chapter 1: Fundamentals",
            "section": "1.1 Introduction"
        }
    ],
    "collection_name": "textbook_chunks"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Python Example Using HTTPX (Async)

```python
import httpx
import asyncio

async def embed_content():
    url = "http://localhost:8000/api/v1/chat/embed"

    payload = {
        "chunks": [
            {
                "content": "ROS 2 is a flexible middleware...",
                "module": "Module 1",
                "chapter": "Chapter 1",
                "section": "1.1 Intro"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

result = asyncio.run(embed_content())
print(result)
```

## Content Format Guidelines

### Recommended Chunk Size

- **Length**: 200-500 words per chunk
- **Detail**: Each chunk should be self-contained and independently meaningful
- **Complexity**: Balance between specificity and generalizability

### Metadata Organization

- **Module**: Top-level organizational unit (e.g., "Module 1: ROS 2 Basics", "Module 2: Humanoid Robotics")
- **Chapter**: Sub-section of a module (e.g., "Chapter 1: Fundamentals", "Chapter 3: Services")
- **Section**: Fine-grained topic (e.g., "1.1 Introduction", "3.2 Action Client Implementation")

### Example Content Structure

```
Module 1: ROS 2 Basics
  Chapter 1: Fundamentals
    Section 1.1: Introduction to ROS 2
    Section 1.2: Core Concepts
    Section 1.3: Key Terminology
  Chapter 2: Nodes and Topics
    Section 2.1: Understanding Nodes
    Section 2.2: Topic-Based Communication
```

## Processing Pipeline

1. **Validation**: Checks chunks list is not empty and each chunk meets requirements
2. **Collection Setup**: Creates Qdrant collection if needed (idempotent)
3. **Embedding**: Generates 1536-dimensional vectors via OpenAI (text-embedding-3-small)
4. **ID Generation**: Creates unique IDs for each chunk (hash-based)
5. **Indexing**: Upserts vectors to Qdrant with metadata payload
6. **Response**: Returns success status and processing metrics

## Performance Considerations

- **Batch Size**: Can handle dozens to hundreds of chunks in a single request
- **Processing Time**: Depends on OpenAI API latency and Qdrant network
- **Vector Dimension**: All vectors are 1536-dimensional (OpenAI standard)
- **Storage**: Each chunk is stored with full metadata for retrieval

## Integration Points

### Used By

- Content ingestion pipeline
- Admin tools for loading textbook content
- Batch content updates

### Uses

- **OpenAI API**: `text-embedding-3-small` model for generating embeddings
- **Qdrant**: Vector database for storage and semantic search
- **FastAPI**: HTTP request/response handling
- **Pydantic**: Request/response validation

## Testing

Run the integration tests:

```bash
pytest backend/tests/integration/test_embed_endpoint.py -v
```

Test data is available in `backend/tests/fixtures/sample_textbook.py`:

```python
from tests.fixtures.sample_textbook import SAMPLE_CHUNKS, MINIMAL_CHUNKS

# SAMPLE_CHUNKS contains 12 realistic passages
# MINIMAL_CHUNKS contains 2 short passages for quick tests
```

## Future Enhancements

- Authentication/authorization for admin endpoint
- Rate limiting for bulk embedding operations
- Progress tracking for large batch operations
- Webhook notifications on completion
- Support for custom embeddings models
- Batch import from file formats (CSV, PDF, etc.)
