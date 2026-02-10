#!/usr/bin/env python3
"""Side-by-side test of ChatService vs HTTP endpoint"""
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import requests
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_comparison():
    print('='*80)
    print('SIDE-BY-SIDE COMPARISON: ChatService vs HTTP Endpoint')
    print('='*80)
    print()

    query = 'Chapter 6'

    # TEST 1: ChatService direct
    print('[TEST 1] ChatService.process_query() directly')
    print('-' * 80)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from src.services.chat_service import get_chat_service

        chat_service = await get_chat_service(session)
        response1 = await chat_service.process_query(query=query)

        print(f'Query: {query}')
        print(f'Passages: {len(response1.retrieved_passages)}')
        for i, p in enumerate(response1.retrieved_passages[:3], 1):
            ch = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
            score = response1.relevance_scores[i-1] if i <= len(response1.relevance_scores) else 0
            print(f'  [{i}] Chapter {ch} (score: {score:.3f})')
        print(f'Response preview: {response1.response[:100]}...')
    print()

    # TEST 2: HTTP endpoint
    print('[TEST 2] HTTP POST /api/v1/chat')
    print('-' * 80)

    response2 = requests.post(
        'http://127.0.0.1:8000/api/v1/chat',
        json={'query': query},
        timeout=30
    ).json()

    print(f'Query: {query}')
    print(f'Passages: {len(response2["retrieved_passages"])}')
    for i, p in enumerate(response2["retrieved_passages"][:3], 1):
        ch = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
        score = response2["relevance_scores"][i-1] if i <= len(response2["relevance_scores"]) else 0
        print(f'  [{i}] Chapter {ch} (score: {score:.3f})')
    print(f'Response preview: {response2["response"][:100]}...')
    print()

    # COMPARISON
    print('[COMPARISON]')
    print('-' * 80)
    ch1_direct = response1.retrieved_passages[0].split('Chapter')[1].strip().split()[0] if 'Chapter' in response1.retrieved_passages[0] else '?'
    ch1_http = response2["retrieved_passages"][0].split('Chapter')[1].strip().split()[0] if 'Chapter' in response2["retrieved_passages"][0] else '?'

    print(f'ChatService returned: Chapter {ch1_direct}')
    print(f'HTTP endpoint returned: Chapter {ch1_http}')
    print()
    if ch1_direct == ch1_http:
        print('RESULT: MATCH - Both return the same chapter')
    else:
        print(f'RESULT: MISMATCH - Different chapters! (Direct={ch1_direct}, HTTP={ch1_http})')

asyncio.run(test_comparison())
