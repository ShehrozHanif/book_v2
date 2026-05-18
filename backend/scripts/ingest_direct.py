#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone textbook ingest script.
Reads .env, parses all chapter markdown files, embeds with OpenAI,
and upserts directly into Qdrant — no local backend required.

Usage:
    cd backend
    venv/Scripts/python scripts/ingest_direct.py
"""

import os
import re
import sys
import hashlib
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# Load .env manually (no python-dotenv required)
# ---------------------------------------------------------------------------
ENV_PATH = Path(__file__).parent.parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

OPENAI_API_KEY     = os.environ.get("OPENAI_API_KEY", "").strip()
QDRANT_URL         = os.environ.get("QDRANT_URL", "").strip()
QDRANT_API_KEY     = os.environ.get("QDRANT_API_KEY", "").strip()
COLLECTION_NAME    = os.environ.get("QDRANT_COLLECTION_NAME", "textbook_chunks")
EMBED_MODEL        = "text-embedding-3-small"
VECTOR_SIZE        = 1536
CHUNK_WORDS        = 400
BATCH_SIZE         = 20

if not OPENAI_API_KEY or not QDRANT_URL or not QDRANT_API_KEY:
    print("[-] Missing OPENAI_API_KEY, QDRANT_URL, or QDRANT_API_KEY in .env")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Lazy imports
# ---------------------------------------------------------------------------
try:
    from openai import OpenAI
except ImportError:
    print("[-] openai package not found. Run: pip install openai")
    sys.exit(1)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("[-] qdrant-client not found. Run: pip install qdrant-client")
    sys.exit(1)

try:
    import frontmatter
except ImportError:
    print("[-] python-frontmatter not found. Run: pip install python-frontmatter")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

TEXTBOOK_PATH = Path(__file__).parent.parent.parent / "frontend" / "textbook-site" / "docs"


def module_for_chapter(n: int) -> str:
    if 1 <= n <= 5:   return "Module 1"
    if 6 <= n <= 10:  return "Module 2"
    if 11 <= n <= 15: return "Module 3"
    if n == 16:       return "Module 4"
    if 17 <= n <= 22: return "Module 5"
    return "Unknown"


def chunk_content(text: str, words: int = CHUNK_WORDS):
    parts = text.split()
    for i in range(0, len(parts), words):
        yield " ".join(parts[i:i + words])


def clean_markdown(text: str) -> str:
    text = re.sub(r"#+\s+", "", text)
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_chunks():
    chapters = sorted(TEXTBOOK_PATH.glob("module-*/chapter-*.md"))
    print(f"[+] Found {len(chapters)} chapter files\n")
    all_chunks = []

    for path in chapters:
        m = re.search(r"chapter-(\d+)", path.name)
        if not m:
            continue
        chapter_num = int(m.group(1))
        module = module_for_chapter(chapter_num)
        chapter_label = f"Chapter {chapter_num}"

        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        title = post.metadata.get("title", path.stem)
        body = clean_markdown(post.content)

        count = 0
        for i, chunk in enumerate(chunk_content(body)):
            if len(chunk.strip()) < 50:
                continue
            enriched = f"{module} {chapter_label}: {title} — {chunk.strip()}"
            all_chunks.append({
                "content": enriched,
                "module": module,
                "chapter": chapter_label,
                "section": f"Section {i + 1}",
            })
            count += 1

        print(f"  {path.name}: {count} chunks")

    print(f"\n[*] Total chunks: {len(all_chunks)}")
    return all_chunks


def ensure_collection():
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
        print(f"[*] Collection '{COLLECTION_NAME}' already exists — will upsert into it")
    except Exception:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"[+] Created collection '{COLLECTION_NAME}'")


def embed_batch(texts):
    response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def chunk_id(content: str) -> int:
    return int(hashlib.md5(content.encode()).hexdigest()[:8], 16)


def ingest(all_chunks):
    ensure_collection()

    total = len(all_chunks)
    indexed = 0

    for start in range(0, total, BATCH_SIZE):
        batch = all_chunks[start:start + BATCH_SIZE]
        texts = [c["content"] for c in batch]

        try:
            vectors = embed_batch(texts)
        except Exception as e:
            print(f"  [-] Embedding error on batch {start // BATCH_SIZE + 1}: {e}")
            continue

        points = [
            PointStruct(
                id=chunk_id(c["content"]),
                vector=v,
                payload={
                    "content": c["content"],
                    "module": c["module"],
                    "chapter": c["chapter"],
                    "section": c["section"],
                },
            )
            for c, v in zip(batch, vectors)
        ]

        try:
            qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
            indexed += len(points)
            print(f"  [+] Batch {start // BATCH_SIZE + 1}: {len(points)} upserted  ({indexed}/{total})")
        except Exception as e:
            print(f"  [-] Qdrant upsert error: {e}")

    print(f"\n{'='*55}")
    print(f"[+] DONE — {indexed}/{total} chunks indexed into '{COLLECTION_NAME}'")
    print(f"{'='*55}")


if __name__ == "__main__":
    print(f"[*] Qdrant: {QDRANT_URL}")
    print(f"[*] Collection: {COLLECTION_NAME}\n")
    chunks = build_chunks()
    ingest(chunks)
