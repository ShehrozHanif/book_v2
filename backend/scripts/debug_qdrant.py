#!/usr/bin/env python3
"""Debug script to check what chapters are indexed in Qdrant."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import asyncio
from qdrant_client import QdrantClient

def main():
    """Query Qdrant and list chapters by frequency."""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    print("[*] Querying Qdrant collection...")

    # Get all points
    collection_info = client.get_collection(collection_name)
    total_points = collection_info.points_count

    print(f"[+] Total points: {total_points}")
    print()

    # Scroll through all points and collect chapters
    chapter_counts = {}
    module_counts = {}

    # Use scroll to get all points
    try:
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=total_points,
        )

        print(f"[+] Retrieved {len(points)} points")
        print()

        # Count by chapter
        for point in points:
            if point.payload:
                chapter = point.payload.get('chapter', 'Unknown')
                module = point.payload.get('module', 'Unknown')

                chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
                module_counts[module] = module_counts.get(module, 0) + 1

        # Print statistics
        print("CHAPTERS INDEXED:")
        print("-" * 60)
        for chapter in sorted(chapter_counts.keys(), key=lambda x: int(x.split()[-1]) if x != 'Unknown' else 999):
            count = chapter_counts[chapter]
            print(f"  {chapter}: {count} chunks")

        print()
        print("MODULES INDEXED:")
        print("-" * 60)
        for module in sorted(module_counts.keys()):
            count = module_counts[module]
            print(f"  {module}: {count} chunks")

        print()
        print("[+] SUMMARY")
        print("-" * 60)
        print(f"  Total indexed: {sum(chapter_counts.values())} chunks")
        print(f"  Unique chapters: {len(chapter_counts)}")
        print(f"  Missing chapters: {set([f'Chapter {i}' for i in range(1, 23)]) - set(chapter_counts.keys())}")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
