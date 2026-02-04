#!/bin/bash

# RAG Indexing Metadata Generator
# Extracts learning objectives, keywords, and section headings for Qdrant indexing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAPTERS_DIR="$SCRIPT_DIR/../textbook/chapters"
METADATA_DIR="$SCRIPT_DIR/../textbook/metadata"
OUTPUT_FILE="$METADATA_DIR/rag-metadata.json"

echo "=== RAG Indexing Metadata Generator ==="
echo "Extracting metadata from chapters for Qdrant indexing..."
echo ""

# Create JSON file header
cat > "$OUTPUT_FILE" << 'JSONHEADER'
{
  "metadata": {
    "version": "1.0",
    "generated": "GENERATED_DATE",
    "purpose": "Qdrant vector database indexing metadata",
    "total_chapters": 0,
    "total_keywords": 0
  },
  "chapters": []
}
JSONHEADER

# Replace date placeholder
sed -i "s/GENERATED_DATE/$(date -u +%Y-%m-%dT%H:%M:%SZ)/" "$OUTPUT_FILE"

echo "Processing chapters..."

# Counters
total_chapters=0
temp_chapters=""

# Process each chapter
for chapter_file in "$CHAPTERS_DIR"/[0-9][0-9]*.md; do
    if [ -f "$chapter_file" ]; then
        filename=$(basename "$chapter_file")
        
        # Extract metadata
        chapter_id=$(sed -n 's/^chapter_id: "\([^"]*\)".*/\1/p' "$chapter_file")
        module=$(sed -n 's/^module: "\([^"]*\)".*/\1/p' "$chapter_file")
        title=$(sed -n 's/^title: "\([^"]*\)".*/\1/p' "$chapter_file")
        
        # Extract learning objectives
        objectives=$(sed -n '/## Learning Objectives/,/^##/p' "$chapter_file" | \
                    grep "^- " | sed 's/^- //' | tr '\n' '|')
        
        # Extract section headings
        sections=$(grep "^## Section" "$chapter_file" | sed 's/^## //' | tr '\n' '|')
        
        # Extract keywords (from first content paragraph)
        keywords=$(sed -n '/^## Introduction/,/^##/p' "$chapter_file" | \
                  head -3 | grep -o '[A-Z][a-z]*' | sort -u | tr '\n' ',' | sed 's/,$//')
        
        # Count code examples
        code_examples=$(grep -c "### Code Example" "$chapter_file" || echo "0")
        
        # Extract word count
        word_count=$(sed '/^---$/,/^---$/d' "$chapter_file" | wc -w)
        
        temp_chapters="$temp_chapters
    {
      \"chapter_id\": $chapter_id,
      \"module\": \"$module\",
      \"title\": \"$title\",
      \"learning_objectives\": \"$objectives\",
      \"sections\": \"$sections\",
      \"keywords\": \"$keywords\",
      \"code_examples_count\": $code_examples,
      \"word_count\": $word_count,
      \"indexed\": false,
      \"embedding_generated\": false
    },"
        
        ((total_chapters++))
        printf "✓ Chapter %s: %s\n" "$chapter_id" "$title"
    fi
done

# Remove trailing comma from last entry and close JSON
if [ -n "$temp_chapters" ]; then
    temp_chapters=$(echo "$temp_chapters" | sed '$ s/,$//')
    # Recreate JSON with chapters
    python3 << PYTHON
import json
import re

# Read existing metadata
with open("$OUTPUT_FILE", "r") as f:
    data = json.load(f)

# Parse and add chapters
chapters_str = """$temp_chapters"""
chapters = []

# Parse chapters manually since they're formatted as JSON array elements
chapter_strs = chapters_str.strip().split('},{')
for i, ch_str in enumerate(chapter_strs):
    if i > 0:
        ch_str = '{' + ch_str
    if i < len(chapter_strs) - 1:
        ch_str = ch_str + '}'
    else:
        ch_str = ch_str.rstrip(',') + '}'
    
    try:
        ch = json.loads(ch_str)
        chapters.append(ch)
    except:
        pass

data['chapters'] = chapters
data['metadata']['total_chapters'] = len(chapters)

# Save updated JSON
with open("$OUTPUT_FILE", "w") as f:
    json.dump(data, f, indent=2)

print(f"Generated metadata for {len(chapters)} chapters")
PYTHON
fi

echo ""
echo "=== Summary ==="
echo "Total chapters processed: $total_chapters"
echo "Output file: $OUTPUT_FILE"
echo ""
echo "✓ Metadata generated for Qdrant indexing"
echo ""
echo "Next steps:"
echo "1. Review metadata in: $OUTPUT_FILE"
echo "2. Generate embeddings using the metadata"
echo "3. Index into Qdrant vector database"
