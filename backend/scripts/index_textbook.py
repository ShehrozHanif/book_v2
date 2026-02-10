#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract chapters from Docusaurus textbook and index them in Qdrant.
Usage: python scripts/index_textbook.py
"""

import os
import re
import json
import asyncio
import httpx
import sys
from pathlib import Path
from typing import List, Dict, Optional
import frontmatter

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
TEXTBOOK_DOCS_PATH = Path(__file__).parent.parent.parent / "frontend" / "textbook-site" / "docs"
BACKEND_URL = "http://127.0.0.1:8000"
EMBED_ENDPOINT = f"{BACKEND_URL}/api/v1/chat/embed"
CHUNK_SIZE = 500  # words per chunk
CHUNK_OVERLAP = 50  # words overlap between chunks

print("[*] Textbook indexing script")
print("[*] Looking for chapters in: {}".format(TEXTBOOK_DOCS_PATH))


def extract_frontmatter_and_content(file_path: Path) -> tuple[Dict, str]:
    """Extract frontmatter and content from markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
        return post.metadata, post.content


def extract_module_chapter_from_path(file_path: Path) -> tuple[Optional[str], Optional[str]]:
    """Extract module and chapter info from file path."""
    # Extract chapter number from filename
    match = re.search(r"chapter-(\d+)", file_path.name)
    if not match:
        return None, None

    chapter_num = int(match.group(1))

    # Determine module based on chapter number
    if 1 <= chapter_num <= 5:
        module_num = 1
    elif 6 <= chapter_num <= 10:
        module_num = 2
    elif 11 <= chapter_num <= 15:
        module_num = 3
    elif chapter_num == 16:
        module_num = 4
    elif 17 <= chapter_num <= 22:
        module_num = 5
    else:
        return None, None

    return f"Module {module_num}", f"Chapter {chapter_num}"


def split_into_chunks(text: str, words_per_chunk: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into chunks by word count with overlap."""
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk_words = words[i:i + words_per_chunk]
        chunk_text = " ".join(chunk_words)

        if chunk_text.strip():
            chunks.append(chunk_text)

        # Move forward with overlap
        i += words_per_chunk - overlap

    return chunks


def get_all_chapter_files() -> List[Path]:
    """Get all chapter markdown files from the textbook."""
    if not TEXTBOOK_DOCS_PATH.exists():
        raise FileNotFoundError(f"Textbook path not found: {TEXTBOOK_DOCS_PATH}")

    chapter_files = []

    # Find all markdown files in module directories
    for module_dir in sorted(TEXTBOOK_DOCS_PATH.glob("module-*")):
        if module_dir.is_dir():
            for chapter_file in sorted(module_dir.glob("chapter-*.md")):
                chapter_files.append(chapter_file)

    return chapter_files


async def index_chapters():
    """Main function to extract and index all chapters."""

    try:
        # Get all chapter files
        chapter_files = get_all_chapter_files()
        print("\n[+] Found {} chapter files".format(len(chapter_files)))

        if not chapter_files:
            print("[-] No chapter files found!")
            return

        all_chunks = []

        # Process each chapter
        for chapter_file in chapter_files:
            print("\n[*] Processing: {}".format(chapter_file.name))

            try:
                # Extract metadata and content
                frontmatter_meta, content = extract_frontmatter_and_content(chapter_file)

                # Get module and chapter info
                module, chapter = extract_module_chapter_from_path(chapter_file)
                title = frontmatter_meta.get("title", chapter_file.stem)

                # Clean up content (remove markdown syntax)
                content = re.sub(r"#+\s+", "", content)  # Remove headers
                content = re.sub(r"\*\*", "", content)  # Remove bold
                content = re.sub(r"__", "", content)  # Remove underscores

                # Split into chunks
                chunks = split_into_chunks(content, words_per_chunk=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
                print("    [+] Split into {} chunks".format(len(chunks)))

                # Create chunk objects with metadata
                for i, chunk_text in enumerate(chunks):
                    if len(chunk_text.strip()) > 50:  # Skip very small chunks
                        # Include metadata prominently for better semantic search
                        # Repeat chapter name to increase semantic weight
                        enriched_content = "{} {} {} - {}".format(
                            module or "Unknown Module",
                            chapter or title,
                            chapter or title,  # Repeat chapter name for emphasis
                            chunk_text.strip()
                        )
                        chunk_obj = {
                            "content": enriched_content,
                            "module": module or "Unknown Module",
                            "chapter": chapter or title,
                            "section": "Section {}".format(i+1),
                            "source": chapter_file.name,
                        }
                        all_chunks.append(chunk_obj)

            except Exception as e:
                print("    [-] Error processing {}: {}".format(chapter_file.name, e))
                continue

        print("\n[*] Total chunks created: {}".format(len(all_chunks)))

        if not all_chunks:
            print("[-] No chunks created!")
            return

        # Send chunks to backend in batches
        batch_size = 10
        total_indexed = 0

        async with httpx.AsyncClient() as client:
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]

                payload = {
                    "chunks": batch,
                    "collection_name": "textbook_chunks"
                }

                try:
                    print("\n[*] Sending batch {} ({} chunks)...".format(i//batch_size + 1, len(batch)))

                    response = await client.post(
                        EMBED_ENDPOINT,
                        json=payload,
                        timeout=60.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        indexed = result.get("indexed_count", len(batch))
                        total_indexed += indexed
                        print("    [+] Successfully indexed {} chunks".format(indexed))
                    else:
                        print("    [-] Error: {}".format(response.status_code))
                        print("    Response: {}".format(response.text))

                except httpx.TimeoutException:
                    print("    [!] Request timeout - server may be processing")
                except Exception as e:
                    print("    [-] Error sending batch: {}".format(e))

        print("\n" + "="*60)
        print("[+] INDEXING COMPLETE!")
        print("[*] Total chunks indexed: {}/{}".format(total_indexed, len(all_chunks)))
        print("="*60)

    except Exception as e:
        print("\n[-] Fatal error: {}".format(e))
        raise


if __name__ == "__main__":
    # Run the async function
    asyncio.run(index_chapters())
