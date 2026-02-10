#!/usr/bin/env python3
"""Test if Qdrant chapter filtering actually works"""
import os
import asyncio
from src.services.embedding_service import get_embedding_service
from src.services.qdrant_client import get_qdrant_service

async def test_filter():
    print("=" * 80)
    print("TESTING QDRANT CHAPTER FILTER")
    print("=" * 80)
    print()
    
    # Get services
    embedding_svc = get_embedding_service()
    qdrant_svc = get_qdrant_service()
    
    # Test 1: Embed "Chapter 4"
    print("TEST 1: Query for 'Chapter 4' (no topic keywords)")
    query_vector = await embedding_svc.embed_query("Chapter 4")
    
    # Search WITHOUT filter
    results_no_filter = await qdrant_svc.search(query_vector, top_k=5)
    print(f"  Without filter: {len(results_no_filter)} results")
    for i, r in enumerate(results_no_filter[:3], 1):
        ch = r['payload'].get('chapter', '?')
        print(f"    [{i}] {ch:20s} (score: {r['score']:.3f})")
    
    # Search WITH filter for Chapter 4
    results_with_filter = await qdrant_svc.search(query_vector, top_k=5, filter_chapter="Chapter 4")
    print(f"  With filter (Chapter 4): {len(results_with_filter)} results")
    for i, r in enumerate(results_with_filter[:3], 1):
        ch = r['payload'].get('chapter', '?')
        print(f"    [{i}] {ch:20s} (score: {r['score']:.3f})")
    
    print()
    print("TEST 2: Query for 'Chapter 4 sensors'")
    query_vector = await embedding_svc.embed_query("Chapter 4 sensors")
    
    # Search WITHOUT filter
    results_no_filter = await qdrant_svc.search(query_vector, top_k=5)
    print(f"  Without filter: {len(results_no_filter)} results")
    for i, r in enumerate(results_no_filter[:3], 1):
        ch = r['payload'].get('chapter', '?')
        print(f"    [{i}] {ch:20s} (score: {r['score']:.3f})")
    
    # Search WITH filter for Chapter 4
    results_with_filter = await qdrant_svc.search(query_vector, top_k=5, filter_chapter="Chapter 4")
    print(f"  With filter (Chapter 4): {len(results_with_filter)} results")
    for i, r in enumerate(results_with_filter[:3], 1):
        ch = r['payload'].get('chapter', '?')
        print(f"    [{i}] {ch:20s} (score: {r['score']:.3f})")
    
    print()
    print("=" * 80)
    print("DIAGNOSIS:")
    print("If both WITH and WITHOUT filter show same results,")
    print("then the Qdrant filter is NOT working!")
    print("=" * 80)

if __name__ == "__main__":
    os.chdir(r"C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend")
    asyncio.run(test_filter())
