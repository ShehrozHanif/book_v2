# RAG Chatbot Chapter Retrieval - Debugging & Fix Notes

## Issue Summary
The chatbot failed to retrieve correct chapters for queries about chapters 4-22, instead returning "no specific information" or wrong chapters (usually Chapter 1).

## Investigation Process

### Step 1: Root Cause Analysis
Ran diagnostic tests comparing:
- Different query types (bare "Chapter X", "Chapter X keywords", "Module X")  
- Direct service calls vs HTTP endpoint
- Single vs multiple test runs

**Finding:** Bare chapter queries ("Chapter 4") returned Chapter 1, while queries with keywords ("Chapter 4 sensors") returned Chapter 4. This indicated the problem was in semantic matching and ranking, not indexing.

### Step 2: Identified Failure Patterns
From comprehensive test results:
- Chapter 1-3: ~50% success (mixed results)
- Chapter 4-22: ~9% success (mostly failing)
- Module queries: 57% success
- Chapter+Topic queries: 80% success
- Generic queries: 100% success

**Hypothesis:** The retrieval system was using Qdrant-level chapter filtering, which returned zero results for bare "Chapter X" queries, triggering a fallback to general search without chapter awareness.

### Step 3: Code Inspection
Found in `retrieval_service.py`:
```python
if not results and filter_chapter:
    logger.info(f"No results with chapter filter, falling back...")
    results = await self.qdrant_service.search(query_vector, top_k=self.top_k)
```

This fallback was returning random chapters because the filter was too strict for low-semantic-similarity queries like "Chapter 4".

## Fixes Applied

### Fix #1: Remove Qdrant-Level Filtering
**File:** `backend/src/services/retrieval_service.py` (lines 195-205)

**Before:**
```python
search_top_k = self.top_k  
if target_chapter:
    filter_chapter = f"Chapter {target_chapter}"
    search_top_k = self.top_k * 2  
results = await self.qdrant_service.search(
    query_vector, top_k=search_top_k, 
    filter_chapter=filter_chapter  # Applied filter here
)
if not results and filter_chapter:
    results = await self.qdrant_service.search(...)  # Fallback
```

**After:**
```python
search_top_k = self.top_k * 5  # Get 25 results instead
results = await self.qdrant_service.search(
    query_vector, top_k=search_top_k,
    filter_chapter=None  # NO FILTER - let semantic similarity guide
)
```

**Impact:** Removed the problematic fallback. Now retrieves 25 results based on semantic similarity alone, letting `rank_passages` prioritize chapters.

### Fix #2: Fix Tuple Unpacking Bug
**File:** `backend/src/services/chat_service.py` (line 159)

**Before:**
```python
for i, (p, s) in enumerate(context_passages, 1):  # WRONG: tries to unpack each string
    ch = p.split('Chapter')[1].strip().split()[0]
```

**After:**
```python
for i, (p, s) in enumerate(zip(context_passages, relevance_scores), 1):  # CORRECT
    ch = p.split('Chapter')[1].strip().split()[0]
```

**Impact:** Fixed "too many values to unpack (expected 2)" validation errors that were preventing proper response formatting.

### Fix #3: Implement Targeted Fallback
**File:** `backend/src/services/retrieval_service.py` (lines 207-227)

Added logic to check if target chapter is in retrieved results:
```python
if target_chapter:
    chapters_in_results = [r['payload'].get('chapter', '') for r in results]
    if not any(target_chapter_str in ch for ch in chapters_in_results):
        # Do targeted search for this specific chapter
        targeted_results = await self.qdrant_service.search(
            query_vector, top_k=5, filter_chapter=target_chapter_str
        )
        if targeted_results:
            results.insert(0, targeted_results[0])
```

**Impact:** Ensures every detected chapter has at least one result in the ranking pool, guaranteeing it will be considered by `rank_passages`.

## Results

### Before Fixes
- Bare chapter queries: 2/22 (9.1%)
- Chapter+Topic queries: 4/5 (80%)
- Module queries: 4/7 (57%)
- Generic queries: 5/5 (100%)

### After Fixes  
- Bare chapter queries: **16/22 (72.7%)** ✓ +63.6pp
- Chapter+Topic queries: **5/5 (100%)** ✓ +20pp
- Module queries: **6/7 (86%)** ✓ +29pp
- Generic queries: **5/5 (100%)** (unchanged)

### Still Failing (6 chapters: 2, 3, 7, 10, 13, 18)
These chapters have inherent low semantic similarity between their chapter name and content. Example:
- Query: "Chapter 2" has similarity ~0.40
- Query: "Chapter 4 sensors" has similarity ~0.54 (keywords boost relevance)

**Possible solutions for remaining failures:**
1. Re-index with richer metadata (e.g., "Chapter 2: Kinematics & Dynamics")
2. Use domain-specific embeddings instead of generic OpenAI embeddings
3. Build explicit chapter-to-keywords mapping

## Testing

Created comprehensive test suite in `COMPREHENSIVE_TEST.py`:
- Tests all 22 chapters with bare queries
- Tests module queries
- Tests chapter+topic combinations  
- Tests generic topic queries
- Saves results to `test_results.json` for analysis

Created diagnostic test in `diagnose_filtering.py`:
- Side-by-side comparison of query types
- Detailed chapter extraction verification
- Score tracking for each result

## Code References

### Key Changes:
1. `backend/src/services/retrieval_service.py:199-205` - Remove filter, increase pool
2. `backend/src/services/retrieval_service.py:207-227` - Add targeted fallback
3. `backend/src/services/chat_service.py:159` - Fix tuple unpacking
4. `backend/src/services/retrieval_service.py:111-155` - `rank_passages` (no changes needed, worked correctly after main fix)

### Related Functions:
- `retrieval_service.extract_chapter_number()` - Detects "Chapter X" in queries (working correctly)
- `retrieval_service.rank_passages()` - Prioritizes target chapter (working correctly after fix)
- `qdrant_client.search()` - Vector search with optional filtering (filter removed from here)

## Lessons Learned

1. **Fallback logic can hide bugs**: The Qdrant filter fallback was masking the real issue
2. **Semantic similarity alone is insufficient**: Need explicit prioritization for structured queries
3. **Multiple ranking layers improve results**: Combining semantic search + chapter prioritization works better than single-pass filtering
4. **Test different query types**: Bare queries vs keyword queries revealed the core issue
5. **Logging is crucial**: Backend logs clearly showed what was being returned at each stage

## Files Modified

- `backend/src/services/retrieval_service.py` - Main fix
- `backend/src/services/chat_service.py` - Bug fix
- Test files created: `COMPREHENSIVE_TEST.py`, `diagnose_filtering.py`, `test_results.json`
