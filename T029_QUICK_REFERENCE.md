# Task T029 Quick Reference

## Implemented Endpoint

```
POST /api/v1/chat/embed
```

## Minimal Working Example

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "chunks": [
      {
        "content": "ROS 2 is a flexible middleware for robot software.",
        "module": "Module 1",
        "chapter": "Chapter 1",
        "section": "1.1 Intro"
      }
    ]
  }'
```

### Response

```json
{
  "success": true,
  "chunks_embedded": 1,
  "collection": "textbook_chunks",
  "message": "Successfully embedded 1 passages into 'textbook_chunks' in 0.45s"
}
```

## File Changes Summary

| File | Change |
|------|--------|
| `backend/src/api/routes/chat.py` | Added endpoint + 3 Pydantic models |
| `backend/src/services/embedding_service.py` | Added `index_textbook()` helper |
| `backend/tests/fixtures/sample_textbook.py` | NEW - Sample test data |
| `backend/tests/integration/test_embed_endpoint.py` | NEW - 12 integration tests |
| `backend/EMBED_ENDPOINT_USAGE.md` | NEW - Usage documentation |

## Key Implementation Details

### 1. Endpoint Location
- **File**: `backend/src/api/routes/chat.py` (lines 194-377)
- **Route**: POST `/api/v1/chat/embed`
- **Function**: `embed_content(request: EmbedRequest) -> EmbedResponse`

### 2. Request Model (EmbedRequest)
- `chunks`: List of TextbookChunk objects (required, min 1)
- `collection_name`: Optional string (default: "textbook_chunks")

### 3. TextbookChunk Fields
- `content`: str, 10-5000 characters
- `module`: str, 1-100 characters
- `chapter`: str, 1-200 characters
- `section`: str, 1-200 characters

### 4. Response Model (EmbedResponse)
- `success`: bool
- `chunks_embedded`: int (count)
- `collection`: str (collection name used)
- `message`: str (status message with timing)

### 5. Processing Steps
1. Validate input
2. Get service instances (EmbeddingService, QdrantService)
3. Create Qdrant collection (idempotent)
4. Convert Pydantic models to dicts
5. Embed passages with OpenAI API
6. Prepare Qdrant points with metadata
7. Upsert points to Qdrant
8. Return success response

### 6. Error Handling
- **400**: Empty chunks list or validation error
- **422**: Invalid field format (Pydantic validation)
- **500**: Embedding or Qdrant failure

## Test Data

Located in `backend/tests/fixtures/sample_textbook.py`:

```python
from tests.fixtures.sample_textbook import SAMPLE_CHUNKS

# SAMPLE_CHUNKS = 12 realistic passages about ROS 2 and Humanoid Robotics
# Each chunk has: content, module, chapter, section
```

## Integration Tests

Located in `backend/tests/integration/test_embed_endpoint.py`:

```bash
pytest backend/tests/integration/test_embed_endpoint.py -v
```

**Test Cases** (12 total):
- Single chunk
- Multiple chunks
- Custom collection name
- Empty chunks (validation)
- Missing required field (validation)
- Invalid chunk format (validation)
- Content too long (validation)
- Response format validation
- Metadata preservation
- Special characters
- Large batch (all 12 samples)

## Helper Function

Added to `backend/src/services/embedding_service.py`:

```python
async def index_textbook(self, chunks: List[dict]) -> int:
    """Embed and index textbook chunks in one call."""
    # Returns: number of chunks indexed
```

## Usage Examples

### Python (Sync)
```python
import requests

url = "http://localhost:8000/api/v1/chat/embed"
payload = {
    "chunks": [
        {
            "content": "ROS 2 is...",
            "module": "Module 1",
            "chapter": "Chapter 1",
            "section": "1.1"
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

### Python (Async)
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/chat/embed",
        json=payload
    )
```

## Verification Checklist

- [x] Endpoint at `/api/v1/chat/embed` (POST)
- [x] Accepts TextbookChunk list
- [x] Creates Qdrant collection if needed
- [x] Embeds via OpenAI API
- [x] Upserts to Qdrant with metadata
- [x] Returns EmbedResponse (success, count, collection, message)
- [x] Error handling (400, 422, 500)
- [x] Comprehensive logging
- [x] Full type hints
- [x] OpenAPI/Swagger documentation
- [x] Sample test data (12 chunks)
- [x] Integration tests (12 test cases)
- [x] Usage documentation

## Documentation Files

- **Usage Guide**: `backend/EMBED_ENDPOINT_USAGE.md`
- **Implementation Summary**: `T029_IMPLEMENTATION_SUMMARY.md`
- **This File**: `T029_QUICK_REFERENCE.md`

## Integration with Existing Services

### OpenAI Integration
- Uses `EmbeddingService.embed_passages()`
- Generates 1536-dim vectors with text-embedding-3-small

### Qdrant Integration
- Uses `QdrantService.create_collection()`
- Uses `QdrantService.upsert()`
- Stores vectors with metadata payload

## Next Steps

1. **Run Integration Tests**: `pytest backend/tests/integration/test_embed_endpoint.py -v`
2. **Load Sample Content**: Use SAMPLE_CHUNKS to populate Qdrant
3. **Test Retrieval**: Query the chat endpoint to verify content retrieval
4. **Load Production Content**: Use endpoint to index actual textbook

## Performance Notes

- **Batch Size**: Can handle dozens to hundreds of chunks per request
- **Vector Dimension**: 1536 (OpenAI standard)
- **Processing Time**: Depends on OpenAI API latency (~500ms-2s typical)
- **Distance Metric**: COSINE (good for semantic similarity)

## Security Notes

- No authentication currently (admin endpoint)
- Input validation via Pydantic models
- SQL injection protection (though not using SQL)
- Content length limits enforced (10-5000 chars)

## Known Limitations

- Collection name in request doesn't override environment variable (by design)
- IDs are hash-based (deterministic)
- No batch progress tracking
- No webhook notifications

## Future Enhancements

- Add authentication/authorization
- Add rate limiting
- Add progress tracking
- Add webhook support
- Support custom embedding models
- Support batch import from files
