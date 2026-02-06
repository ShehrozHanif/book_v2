#!/usr/bin/env python3
"""Comprehensive test suite for chatbot functionality"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/chat"

def test_query(query, description=""):
    """Test a single query"""
    try:
        response = requests.post(
            BASE_URL,
            json={'query': query},
            timeout=30
        )

        data = response.json()
        passages = data.get('retrieved_passages', [])
        scores = data.get('relevance_scores', [])
        response_text = data.get('response', '')

        # Extract chapters from passages
        chapters = []
        for p in passages[:3]:
            if 'Chapter' in p:
                try:
                    ch = p.split('Chapter')[1].strip().split()[0]
                    chapters.append(ch)
                except:
                    chapters.append('?')

        # Determine if response is informative
        has_info = 'no specific information' not in response_text.lower() and 'no information' not in response_text.lower()

        return {
            'query': query,
            'description': description,
            'chapters': chapters,
            'scores': [f"{s:.2f}" for s in scores[:3]],
            'has_info': has_info,
            'response': response_text[:100]
        }
    except Exception as e:
        return {
            'query': query,
            'description': description,
            'error': str(e)
        }

print("="*80)
print("COMPREHENSIVE CHATBOT TEST SUITE")
print("="*80)
print()

# Wait for backend
time.sleep(2)

# Test 1: All chapters (1-22)
print("TEST 1: All Chapters (1-22)")
print("-"*80)
results_chapters = []
for ch in range(1, 23):
    result = test_query(f"Chapter {ch}", f"Chapter {ch}")
    results_chapters.append(result)

    # Extract expected chapter
    expected_ch = str(ch)
    actual_ch = result['chapters'][0] if result['chapters'] else '?'
    match = expected_ch == actual_ch
    status = "[OK]" if match else "[WRONG]"

    print(f"{status} Ch{ch:2d}: Got Ch{actual_ch:2s}, Scores: {result['scores']}, HasInfo: {result['has_info']}")

# Statistics
correct_chapters = sum(1 for r in results_chapters if r['chapters'] and r['chapters'][0] == str(results_chapters.index(r) + 1))
print(f"\nChapter Success Rate: {correct_chapters}/22")
print()

# Test 2: Module queries
print("TEST 2: Module Queries")
print("-"*80)
module_queries = [
    ("Module 1", "Information about Module 1"),
    ("Module 2", "Information about Module 2"),
    ("Module 3", "Information about Module 3"),
    ("Module 4", "Information about Module 4"),
    ("Module 5", "Information about Module 5"),
    ("Explain Module 1", "Explain what is in Module 1"),
    ("What is in Module 2", "Question about Module 2 content"),
]

results_modules = []
for query, desc in module_queries:
    result = test_query(query, desc)
    results_modules.append(result)

    status = "[OK]" if result.get('has_info') else "[NO INFO]"
    print(f"{status} '{query}': Chapters={result.get('chapters', [])}, HasInfo={result.get('has_info')}")

print()

# Test 3: Specific chapter with content keywords
print("TEST 3: Chapter + Topic Queries")
print("-"*80)
topic_queries = [
    "Chapter 1 humanoid robotics definition",
    "Chapter 4 sensors IMU",
    "Chapter 6 action servers ROS",
    "Chapter 11 learning algorithms",
    "Chapter 22 getting started project",
]

results_topics = []
for query in topic_queries:
    result = test_query(query, "Chapter + topic")
    results_topics.append(result)

    ch_num = query.split('Chapter ')[1].split()[0] if 'Chapter' in query else '?'
    actual_ch = result['chapters'][0] if result['chapters'] else '?'
    match = ch_num == actual_ch
    status = "[OK]" if match and result.get('has_info') else "[PARTIAL]"

    print(f"{status} '{query}': Got Ch{actual_ch}, HasInfo={result.get('has_info')}")

print()

# Test 4: Generic topic queries (should work)
print("TEST 4: Generic Topic Queries (baseline)")
print("-"*80)
generic_queries = [
    "What is humanoid robotics",
    "Explain kinematics",
    "What is ROS 2",
    "Tell me about sensors",
    "What is dynamics",
]

results_generic = []
for query in generic_queries:
    result = test_query(query, "Generic topic")
    results_generic.append(result)

    status = "[OK]" if result.get('has_info') else "[NO INFO]"
    print(f"{status} '{query}': Chapters={result.get('chapters', [])}, HasInfo={result.get('has_info')}")

print()

# Summary Report
print("="*80)
print("SUMMARY REPORT")
print("="*80)

print(f"\n1. CHAPTER QUERIES (1-22):")
correct = sum(1 for i, r in enumerate(results_chapters) if r['chapters'] and r['chapters'][0] == str(i + 1))
informative = sum(1 for r in results_chapters if r.get('has_info'))
print(f"   - Correct chapter retrieved: {correct}/22")
print(f"   - Informative responses: {informative}/22")
print(f"   - Success rate: {correct}/22 ({100*correct/22:.1f}%)")

print(f"\n2. MODULE QUERIES:")
informative_modules = sum(1 for r in results_modules if r.get('has_info'))
print(f"   - Informative responses: {informative_modules}/7")

print(f"\n3. CHAPTER + TOPIC QUERIES:")
correct_topics = sum(1 for query, r in zip(topic_queries, results_topics)
                     if 'Chapter' in query and r['chapters'] and r['chapters'][0] == query.split('Chapter ')[1].split()[0])
informative_topics = sum(1 for r in results_topics if r.get('has_info'))
print(f"   - Correct chapter retrieved: {correct_topics}/5")
print(f"   - Informative responses: {informative_topics}/5")

print(f"\n4. GENERIC QUERIES:")
informative_generic = sum(1 for r in results_generic if r.get('has_info'))
print(f"   - Informative responses: {informative_generic}/5")

print()
print("="*80)

# Save results to file
with open('test_results.json', 'w') as f:
    json.dump({
        'chapters': results_chapters,
        'modules': results_modules,
        'topics': results_topics,
        'generic': results_generic,
        'summary': {
            'chapter_success_rate': f"{correct}/22",
            'module_success_rate': f"{informative_modules}/7",
            'topic_success_rate': f"{correct_topics}/5 correct, {informative_topics}/5 informative",
            'generic_success_rate': f"{informative_generic}/5"
        }
    }, f, indent=2)

print("\nDetailed results saved to: test_results.json")
