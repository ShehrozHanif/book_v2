#!/usr/bin/env python3
"""Test ChatService directly to isolate the problem"""
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_chat_service():
    print('='*80)
    print('TESTING CHATSERVICE DIRECTLY (Chapter 6)')
    print('='*80)
    print()

    # Create async session
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from src.services.chat_service import get_chat_service

        chat_service = await get_chat_service(session)

        query = 'Chapter 6'
        print(f'[TEST] Calling chat_service.process_query("{query}")')
        print()

        response = await chat_service.process_query(
            query=query,
            conversation_id=None,
            user_id=None
        )

        print(f'[RESULT]')
        print(f'  Passages retrieved: {len(response.retrieved_passages)}')

        for i, passage in enumerate(response.retrieved_passages, 1):
            if 'Chapter' in passage:
                ch = passage.split('Chapter')[1].strip().split()[0]
            else:
                ch = '?'
            score = response.relevance_scores[i-1]
            print(f'    [{i}] Chapter {ch} (score: {score:.3f})')

        print()
        print(f'  Response text (first 150 chars):')
        print(f'    {response.response[:150]}...')

asyncio.run(test_chat_service())
