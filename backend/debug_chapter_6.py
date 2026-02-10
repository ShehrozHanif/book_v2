#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio

async def debug_chapter_6():
    print('='*80)
    print('DEBUGGING CHAPTER 6 QUERY - STEP BY STEP')
    print('='*80)
    print()

    from src.services.embedding_service import get_embedding_service
    from src.services.retrieval_service import get_retrieval_service
    from src.services.qdrant_client import get_qdrant_service

    embedding_svc = get_embedding_service()
    retrieval_svc = get_retrieval_service()
    qdrant_svc = get_qdrant_service()

    query = 'Chapter 6'

    # Step 1: Chapter detection
    print('[STEP 1] Chapter extraction')
    chapter_num = retrieval_svc.extract_chapter_number(query)
    print(f'  Result: {chapter_num}')
    print()

    # Step 2: Embed query
    print('[STEP 2] Embedding query')
    query_vector = await embedding_svc.embed_query(query)
    print(f'  Vector created (size: {len(query_vector)})')
    print()

    # Step 3: Search WITH filter
    print('[STEP 3] Qdrant search WITH "Chapter 6" filter (top_k=10)')
    filtered_results = await qdrant_svc.search(
        query_vector,
        top_k=10,
        filter_chapter='Chapter 6'
    )
    print(f'  Returned {len(filtered_results)} results')
    if filtered_results:
        chapters_in_filter = {}
        for r in filtered_results:
            ch = r['payload'].get('chapter')
            chapters_in_filter[ch] = chapters_in_filter.get(ch, 0) + 1
        for ch in sorted(chapters_in_filter.keys()):
            print(f'    - {ch}: {chapters_in_filter[ch]} chunks')
    print()

    # Step 4: Search WITHOUT filter
    print('[STEP 4] Qdrant search WITHOUT filter (top_k=10)')
    general_results = await qdrant_svc.search(query_vector, top_k=10)
    print(f'  Returned {len(general_results)} results')
    if general_results:
        chapters_general = {}
        for r in general_results:
            ch = r['payload'].get('chapter')
            chapters_general[ch] = chapters_general.get(ch, 0) + 1
        for ch in sorted(chapters_general.keys()):
            scores_for_ch = [r['score'] for r in general_results if r['payload'].get('chapter') == ch]
            top_score = max(scores_for_ch)
            print(f'    - {ch}: {chapters_general[ch]} chunks (top score: {top_score:.3f})')
    print()

    # Step 5: Call retrieve_context
    print('[STEP 5] retrieve_context(query="Chapter 6", top_k=3)')
    passages, scores = await retrieval_svc.retrieve_context(
        query_vector=query_vector,
        query=query,
        top_k=3
    )
    print(f'  Returned {len(passages)} passages')
    for i, p in enumerate(passages, 1):
        ch_match = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
        print(f'    [{i}] Chapter {ch_match} (score: {scores[i-1]:.3f})')
        print(f'        Preview: {p[:100]}...')

asyncio.run(debug_chapter_6())
