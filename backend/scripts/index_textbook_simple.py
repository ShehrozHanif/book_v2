#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple synchronous script to index textbook chapters.
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import requests
    import frontmatter
except ImportError:
    print("[-] Installing required packages...")
    os.system('python -m pip install requests python-frontmatter -q')
    import requests
    import frontmatter

# Config
TEXTBOOK_PATH = Path(__file__).parent.parent.parent / "frontend" / "textbook-site" / "docs"
API_URL = "http://127.0.0.1:8000"
CHUNK_SIZE = 500

print("[*] Starting textbook indexing...")
print("[*] Textbook path: {}".format(TEXTBOOK_PATH))

# Find chapters
chapters = sorted(TEXTBOOK_PATH.glob("module-*/chapter-*.md"))
print("[+] Found {} chapters".format(len(chapters)))

if not chapters:
    print("[-] No chapters found!")
    sys.exit(1)

all_chunks = []

# Process each chapter
for i, chapter_file in enumerate(chapters, 1):
    print("\n[{}/{}] Processing: {}".format(i, len(chapters), chapter_file.name))

    try:
        # Read file
        with open(chapter_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Extract metadata
        title = post.metadata.get('title', chapter_file.stem)
        content = post.content

        # Parse chapter number from filename
        chapter_num = int(re.search(r'chapter-(\d+)', chapter_file.name).group(1))

        # Determine module based on chapter number
        if 1 <= chapter_num <= 5:
            module = "Module 1"
        elif 6 <= chapter_num <= 10:
            module = "Module 2"
        elif 11 <= chapter_num <= 15:
            module = "Module 3"
        elif chapter_num == 16:
            module = "Module 4"
        elif 17 <= chapter_num <= 22:
            module = "Module 5"
        else:
            module = "Unknown"

        chapter = "Chapter {}".format(chapter_num)

        # Clean content
        content = re.sub(r'#+\s+', '', content)
        content = re.sub(r'\*\*', '', content)
        content = re.sub(r'__', '', content)

        # Split into chunks
        words = content.split()
        for j in range(0, len(words), CHUNK_SIZE):
            chunk_words = words[j:j+CHUNK_SIZE]
            chunk_text = ' '.join(chunk_words).strip()

            if len(chunk_text) > 50:
                # Include metadata prominently for better semantic search
                # Repeat chapter name to increase semantic weight
                enriched_content = "{} {} {} - {}".format(
                    module,
                    chapter,
                    chapter,  # Repeat chapter name for emphasis
                    chunk_text
                )
                all_chunks.append({
                    "content": enriched_content,
                    "module": module,
                    "chapter": chapter,
                    "section": "Section {}".format(j//CHUNK_SIZE + 1),
                    "source": chapter_file.name,
                })

        print("[+] Created {} chunks".format(len([c for c in all_chunks if c['chapter'] == chapter])))

    except Exception as e:
        print("[-] Error: {}".format(e))

print("\n[*] Total chunks: {}".format(len(all_chunks)))

if not all_chunks:
    print("[-] No chunks created!")
    sys.exit(1)

# Upload to backend
print("\n[*] Uploading to backend...")
batch_size = 10
total_indexed = 0

for i in range(0, len(all_chunks), batch_size):
    batch = all_chunks[i:i+batch_size]

    try:
        response = requests.post(
            "{}/api/v1/chat/embed".format(API_URL),
            json={"chunks": batch, "collection_name": "textbook_chunks"},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            indexed = result.get('indexed_count', len(batch))
            total_indexed += indexed
            print("[+] Batch {}: {} chunks indexed".format(i//batch_size + 1, indexed))
        else:
            print("[-] Batch {}: Error {}".format(i//batch_size + 1, response.status_code))
            print("    Response: {}".format(response.text[:200]))

    except Exception as e:
        print("[-] Batch {}: {}".format(i//batch_size + 1, e))

print("\n" + "="*60)
print("[+] COMPLETE!")
print("[*] Indexed {}/{} chunks".format(total_indexed, len(all_chunks)))
print("="*60)
