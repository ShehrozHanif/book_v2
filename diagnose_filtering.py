#!/usr/bin/env python3
"""Diagnose why chapter filtering is failing"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/chat"

test_queries = [
    ("Chapter 1", "Should work - baseline"),
    ("Chapter 4", "Should fail - returns Ch1"),
    ("Chapter 6", "Should fail - returns Ch1"),
    ("Chapter 4 sensors", "Should work - returns Ch4"),
    ("Chapter 6 ROS", "Should work - returns Ch6"),
]

print("=" * 80)
print("DIAGNOSING CHAPTER FILTERING ISSUE")
print("=" * 80)
print()

for query, desc in test_queries:
    print(f"Query: {query:30s} ({desc})")
    print("-" * 80)
    
    try:
        response = requests.post(BASE_URL, json={'query': query}, timeout=60)
        data = response.json()
        
        passages = data.get('retrieved_passages', [])
        scores = data.get('relevance_scores', [])
        
        print(f"Passages retrieved: {len(passages)}")
        print(f"Scores: {[f'{s:.3f}' for s in scores[:3]]}")
        
        for i, (p, s) in enumerate(zip(passages[:3], scores[:3]), 1):
            ch = p.split('Chapter')[1].strip().split()[0] if 'Chapter' in p else '?'
            preview = p[:80].replace('\n', ' ')
            print(f"  [{i}] Ch{ch:2s} (score: {s:.3f}) | {preview}...")
        
        print()
        
    except Exception as e:
        print(f"  ERROR: {str(e)[:100]}")
        print()
    
    time.sleep(1)

print("=" * 80)
print("ANALYSIS:")
print("- Bare chapter queries return wrong chapters")
print("- Chapter + keywords queries return correct chapters")
print("- This suggests chapter filtering is not working for bare queries")
print("=" * 80)
