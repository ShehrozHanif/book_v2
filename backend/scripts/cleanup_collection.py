#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to delete and recreate the Qdrant collection for re-indexing.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.qdrant_client import get_qdrant_service

async def cleanup():
    """Delete existing collection to prepare for re-indexing."""
    try:
        qdrant_service = get_qdrant_service()

        print("[*] Deleting existing Qdrant collection...")
        await qdrant_service.delete_collection()
        print("[+] Collection deleted successfully")

        print("[*] Creating new collection...")
        await qdrant_service.create_collection()
        print("[+] Collection created successfully")

        print("\n[+] Ready for re-indexing!")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(cleanup())
