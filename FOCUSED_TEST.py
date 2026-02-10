#!/usr/bin/env python3
"""Focused test to identify the exact problem"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/chat"

# Test specific chapters side-by-side
test_cases = [
    # (query, expected_chapter, description)
    ("Chapter 1", "1", "Chapter 1 only"),
    ("Chapter 4", "4", "Chapter 4 only"),
    ("Chapter 6", "6", "Chapter 6 only"),
    ("Chapter 22", "22", "Chapter 22 only"),

    ("Chapter 1 humanoid robotics", "1", "Chapter 1 + topic"),
    ("Chapter 4 sensors", "4", "Chapter 4 + topic"),
    ("Chapter 6 ROS", "6", "Chapter 6 + topic"),
    ("Chapter 22 project", "22", "Chapter 22 + topic"),

    ("Module 1", "1", "Module 1"),
    ("Module 5", "5", "Module 5"),

    ("What is humanoid robotics", "1", "Generic topic"),
    ("Tell me about sensors", "4", "Generic topic"),
]

print("=" * 80)
print("FOCUSED TEST SUITE - Finding the Exact Problem")
print("=" * 80)
print()

results = []
for query, expected, desc in test_cases:
    try:
        time.sleep(0.5)
        response = requests.post(BASE_URL, json={'query': query}, timeout=30)
        data = response.json()

        passages = data.get('retrieved_passages', [])
        scores = data.get('relevance_scores', [])
        response_text = data.get('response', '')

        # Extract chapter from first passage
        actual = '?'
        if passages and 'Chapter' in passages[0]:
            try:
                actual = passages[0].split('Chapter')[1].strip().split()[0]
            except:
                pass

        has_info = 'no specific information' not in response_text.lower() and 'no information' not in response_text.lower()
        match = actual == expected

        result = {
            'query': query,
            'expected': expected,
            'actual': actual,
            'match': match,
            'score': float(scores[0]) if scores else 0,
            'has_info': has_info,
            'desc': desc
        }
        results.append(result)

        status = "[PASS]" if match else "[FAIL]"
        print(f"{status} {desc:25s} | Query: {query:40s} | Expected: Ch{expected}, Got: Ch{actual}, Score: {scores[0] if scores else 0:.2f}, Info: {has_info}")

    except Exception as e:
        print(f"[ERROR] {desc:25s} | {str(e)[:60]}")

print()
print("=" * 80)
print("SUMMARY BY CATEGORY")
print("=" * 80)

# Analyze results by category
chapter_only = [r for r in results if 'Chapter' in r['query'] and '+' not in r['query']]
chapter_topic = [r for r in results if 'Chapter' in r['query'] and '+' not in r['query'] and any(w in r['query'].lower() for w in ['humanoid', 'sensors', 'ros', 'project'])]
chapter_topic = [r for r in results if 'Chapter' in r['query'] and (len(r['query'].split()) > 1)]
modules = [r for r in results if 'Module' in r['query']]
generic = [r for r in results if 'Module' not in r['query'] and 'Chapter' not in r['query']]

if chapter_only:
    print(f"\nChapter-Only Queries: {sum(1 for r in chapter_only if r['match'])}/{len(chapter_only)}")
    for r in chapter_only:
        print(f"  {'✓' if r['match'] else '✗'} {r['query']:30s} -> Expected Ch{r['expected']}, Got Ch{r['actual']}")

if chapter_topic:
    print(f"\nChapter + Topic Queries: {sum(1 for r in chapter_topic if r['match'])}/{len(chapter_topic)}")
    for r in chapter_topic:
        print(f"  {'✓' if r['match'] else '✗'} {r['query']:30s} -> Expected Ch{r['expected']}, Got Ch{r['actual']}")

if modules:
    print(f"\nModule Queries: {sum(1 for r in modules if r['has_info'])}/{len(modules)}")
    for r in modules:
        print(f"  {'✓' if r['has_info'] else '✗'} {r['query']:30s} -> Has Info: {r['has_info']}")

if generic:
    print(f"\nGeneric Queries: {sum(1 for r in generic if r['has_info'])}/{len(generic)}")
    for r in generic:
        print(f"  {'✓' if r['has_info'] else '✗'} {r['query']:30s} -> Expected Ch{r['expected']}, Got Ch{r['actual']}, Info: {r['has_info']}")

print()
print("=" * 80)

# Save results
with open('focused_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: focused_test_results.json")
