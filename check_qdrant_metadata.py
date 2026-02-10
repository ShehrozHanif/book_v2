#!/usr/bin/env python3
"""Check what chapter metadata is actually stored in Qdrant"""
from qdrant_client import QdrantClient

def check_qdrant():
    # Connect to Qdrant
    client = QdrantClient(
        url="https://f251d0a7-4736-4446-acdc-0953570ad2e3.us-east4-0.gcp.cloud.qdrant.io:6333",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.A2hM8Hz9-GBNEBsUuYbx6Pqw0ESHrMTpcfGDixLJv_Q",
        prefer_grpc=False
    )
    
    print("=" * 80)
    print("CHECKING QDRANT METADATA")
    print("=" * 80)
    print()
    
    try:
        # Get collection info
        info = client.get_collection("textbook_chunks")
        print(f"Collection: textbook_chunks")
        print(f"Total vectors: {info.points_count}")
        print()
        
        # Scroll through and examine payloads
        print("Scanning all points to check metadata distribution...")
        print()
        
        all_points = []
        offset = 0
        while True:
            points, next_offset = client.scroll(
                collection_name="textbook_chunks",
                limit=50,
                offset=offset
            )
            if not points:
                break
            all_points.extend(points)
            offset = next_offset
        
        chapter_mapping = {}
        for point in all_points:
            payload = point.payload
            chapter = payload.get("chapter", "UNKNOWN")
            if chapter not in chapter_mapping:
                chapter_mapping[chapter] = 0
            chapter_mapping[chapter] += 1
        
        print("=" * 80)
        print("CHAPTER DISTRIBUTION (ALL POINTS):")
        print("=" * 80)
        for ch in sorted(chapter_mapping.keys()):
            count = chapter_mapping[ch]
            percentage = (count / len(all_points)) * 100
            print(f"  {ch:20s}: {count:3d} chunks ({percentage:5.1f}%)")
        
        total_chapters = len(chapter_mapping)
        print()
        print(f"Total unique chapters: {total_chapters}")
        print(f"Total chunks indexed: {len(all_points)}")
        
        if total_chapters >= 22:
            print("\n[OK] All 22 chapters are indexed!")
        else:
            print(f"\n[ERROR] Only {total_chapters} chapters indexed (expected 22)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_qdrant()
