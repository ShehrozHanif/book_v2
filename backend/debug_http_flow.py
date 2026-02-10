#!/usr/bin/env python3
"""Debug the full HTTP flow from endpoint to retrieval"""
import requests
import json

print('='*80)
print('DEBUGGING HTTP ENDPOINT FOR CHAPTER 6')
print('='*80)
print()

query = 'Chapter 6'
print(f'[REQUEST] POST /api/v1/chat')
print(f'  Query: {query}')
print()

response = requests.post(
    'http://127.0.0.1:8000/api/v1/chat',
    json={'query': query},
    timeout=30
)

data = response.json()

print(f'[RESPONSE] Status: {response.status_code}')
print()

print('Retrieved passages:')
passages = data['retrieved_passages']
scores = data['relevance_scores']

for i, (passage, score) in enumerate(zip(passages, scores), 1):
    # Extract chapter
    if 'Chapter' in passage:
        ch = passage.split('Chapter')[1].strip().split()[0]
    else:
        ch = '?'

    print(f'  [{i}] Chapter {ch} (score: {score:.3f})')
    print(f'      Preview: {passage[:100]}...')
    print()

print('Chatbot response:')
print(f'  {data["response"][:200]}...')
print()

print('ANALYSIS:')
print('  Expected: Chapter 6 passages')
print(f'  Got: Chapter {passages[0].split("Chapter")[1].split()[0] if "Chapter" in passages[0] else "?"} passages')
print(f'  Match: {"YES" if "Chapter 6" in passages[0] else "NO"}')
