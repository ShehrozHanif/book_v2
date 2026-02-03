#!/bin/bash
#
# generate-rag-metadata.sh - RAG Indexing Metadata Generator
#
# Purpose: Reads chapter files and generates chapter-level metadata for Qdrant indexing
# Extracts: learning objectives, keywords, section headings, word counts
#
# Usage: ./generate-rag-metadata.sh [OPTIONS]
#
# Options:
#   -c, --chapter <file>   Process single chapter file
#   -a, --all              Process all chapters in textbook/chapters/
#   -o, --output <file>    Output JSON file (default: textbook/metadata/rag-metadata.json)
#   -h, --help             Show this help message
#
# Example:
#   ./generate-rag-metadata.sh --all
#   ./generate-rag-metadata.sh --chapter textbook/chapters/01-what-is-humanoid-robotics.md
#
# Requirements:
#   - jq (JSON processor)
#   - Chapter files in markdown format with YAML front matter
#
# Author: Content Writing Automation (Spec 002)
# Date: 2026-02-03

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHAPTERS_DIR="$PROJECT_ROOT/textbook/chapters"
OUTPUT_FILE="$PROJECT_ROOT/textbook/metadata/rag-metadata.json"
METADATA_DIR="$PROJECT_ROOT/textbook/metadata"
PROCESS_ALL=false
CHAPTER_FILE=""

# Help text
show_help() {
    cat << EOF
RAG Indexing Metadata Generator

Purpose: Generates chapter-level metadata for RAG indexing into Qdrant

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -c, --chapter <file>    Process single chapter file
    -a, --all               Process all chapters in textbook/chapters/
    -o, --output <file>     Output JSON file (default: textbook/metadata/rag-metadata.json)

EXAMPLES:
    $0 --all
    $0 --chapter textbook/chapters/01-what-is-humanoid-robotics.md
    $0 --all --output custom-metadata.json

OUTPUT FORMAT:
    {
      "chapters": [
        {
          "chapter_id": "01",
          "title": "What is a Humanoid Robot?",
          "module": 1,
          "file_path": "textbook/chapters/01-what-is-humanoid-robotics.md",
          "word_count": 2345,
          "learning_objectives": ["Objective 1", "Objective 2"],
          "keywords": ["humanoid", "robot", "kinematics"],
          "sections": ["Introduction", "Key Concepts", "Summary"],
          "code_examples": ["chapter_01_example_01", "chapter_01_example_02"],
          "indexed_date": "2026-02-03",
          "ready_for_indexing": true
        }
      ]
    }

REQUIREMENTS:
    - jq installed (for JSON processing)
    - Chapter files with YAML front matter

EOF
}

# Error handler
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Info handler
info() {
    echo -e "${GREEN}INFO: $1${NC}"
}

# Warning handler
warn() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--chapter)
                CHAPTER_FILE="$2"
                shift 2
                ;;
            -a|--all)
                PROCESS_ALL=true
                shift
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1. Use --help for usage information."
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    # Check jq is installed
    if ! command -v jq &> /dev/null; then
        error "jq is not installed. Please install jq to use this script."
    fi

    # Check if either --all or --chapter specified
    if [[ "$PROCESS_ALL" == false && -z "$CHAPTER_FILE" ]]; then
        error "Either --all or --chapter must be specified. Use --help for usage."
    fi

    # If single chapter, check it exists
    if [[ -n "$CHAPTER_FILE" && ! -f "$CHAPTER_FILE" ]]; then
        error "Chapter file not found: $CHAPTER_FILE"
    fi

    # Create metadata directory if doesn't exist
    mkdir -p "$METADATA_DIR"
}

# Extract front matter from markdown file
extract_front_matter() {
    local file="$1"
    local key="$2"

    # Extract YAML front matter between --- delimiters
    awk '/^---$/,/^---$/' "$file" | grep "^$key:" | sed "s/^$key: *//; s/\"//g; s/'//g"
}

# Extract learning objectives (list format)
extract_learning_objectives() {
    local file="$1"

    # Look for ## Learning Objectives section
    # Extract bullet points after it
    awk '/^## Learning Objectives/,/^## [^L]/ {
        if ($0 ~ /^- \[.\]/) {
            gsub(/^- \[.\] /, "");
            print $0
        }
    }' "$file" | head -10
}

# Extract section headings (## level)
extract_sections() {
    local file="$1"

    grep "^## " "$file" | sed 's/^## //' | grep -v "^Learning Objectives$"
}

# Extract keywords from text (simple approach: most common significant words)
extract_keywords() {
    local file="$1"

    # Simple keyword extraction: look for capitalized words and technical terms
    # This is a basic implementation; real keyword extraction would use NLP
    grep -oE '\b[A-Z][a-z]+\b' "$file" | sort | uniq -c | sort -rn | head -10 | awk '{print $2}'
}

# Extract code example references
extract_code_examples() {
    local file="$1"

    # Look for code example references in format: chapter_XX_example_YY
    grep -oE 'chapter_[0-9]{2}_example_[0-9]{2}' "$file" | sort -u
}

# Count words in markdown (excluding front matter and code blocks)
count_words() {
    local file="$1"

    # Remove front matter, code blocks, and count words
    awk '
        /^```/ { in_code=!in_code; next }
        /^---$/ { if (++count <= 2) next }
        !in_code && count >= 2 { print }
    ' "$file" | wc -w
}

# Process single chapter file
process_chapter() {
    local file="$1"
    local filename=$(basename "$file")

    info "Processing: $filename"

    # Extract chapter ID from filename (assumes format: XX-title.md)
    local chapter_id=$(echo "$filename" | grep -oE '^[0-9]{2}')

    # Extract metadata
    local title=$(extract_front_matter "$file" "title" || echo "Unknown")
    local module=$(extract_front_matter "$file" "module" || echo "0")
    local word_count=$(count_words "$file")

    # Extract learning objectives
    local objectives=$(extract_learning_objectives "$file" | jq -R . | jq -s .)
    if [[ "$objectives" == "[]" ]]; then
        objectives='["No objectives defined"]'
    fi

    # Extract sections
    local sections=$(extract_sections "$file" | jq -R . | jq -s .)
    if [[ "$sections" == "[]" ]]; then
        sections='["No sections defined"]'
    fi

    # Extract keywords
    local keywords=$(extract_keywords "$file" | head -5 | jq -R . | jq -s .)
    if [[ "$keywords" == "[]" ]]; then
        keywords='["humanoid", "robot", "robotics"]'
    fi

    # Extract code examples
    local code_examples=$(extract_code_examples "$file" | jq -R . | jq -s .)
    if [[ "$code_examples" == "[]" ]]; then
        code_examples='[]'
    fi

    # Check if ready for indexing (has content and objectives)
    local ready_for_indexing="false"
    if [[ $word_count -gt 1000 && "$objectives" != '["No objectives defined"]' ]]; then
        ready_for_indexing="true"
    fi

    # Get current date
    local indexed_date=$(date +%Y-%m-%d)

    # Build JSON object
    cat << EOF
{
  "chapter_id": "$chapter_id",
  "title": "$title",
  "module": $module,
  "file_path": "$file",
  "word_count": $word_count,
  "learning_objectives": $objectives,
  "keywords": $keywords,
  "sections": $sections,
  "code_examples": $code_examples,
  "indexed_date": "$indexed_date",
  "ready_for_indexing": $ready_for_indexing
}
EOF
}

# Process all chapters
process_all_chapters() {
    local chapter_files=()

    # Find all chapter markdown files (excluding template)
    while IFS= read -r -d '' file; do
        local filename=$(basename "$file")
        if [[ "$filename" != "_"* ]]; then
            chapter_files+=("$file")
        fi
    done < <(find "$CHAPTERS_DIR" -name "*.md" -type f -print0 2>/dev/null)

    if [[ ${#chapter_files[@]} -eq 0 ]]; then
        warn "No chapter files found in $CHAPTERS_DIR"
        echo '{"chapters": []}'
        return
    fi

    info "Found ${#chapter_files[@]} chapter file(s)"

    # Process each chapter
    local chapter_json=""
    for file in "${chapter_files[@]}"; do
        local json=$(process_chapter "$file")
        if [[ -n "$chapter_json" ]]; then
            chapter_json="$chapter_json,"
        fi
        chapter_json="$chapter_json$json"
    done

    # Build final JSON
    echo "{\"chapters\": [$chapter_json]}"
}

# Main execution
main() {
    parse_args "$@"
    validate_inputs

    info "Generating RAG indexing metadata..."

    # Process chapters
    if [[ "$PROCESS_ALL" == true ]]; then
        metadata_json=$(process_all_chapters)
    else
        metadata_json="{\"chapters\": [$(process_chapter "$CHAPTER_FILE")]}"
    fi

    # Pretty print and save to file
    echo "$metadata_json" | jq '.' > "$OUTPUT_FILE"

    # Summary
    local chapter_count=$(echo "$metadata_json" | jq '.chapters | length')
    local ready_count=$(echo "$metadata_json" | jq '[.chapters[] | select(.ready_for_indexing == true)] | length')

    info "Metadata generation complete!"
    info "Output file: $OUTPUT_FILE"
    info "Total chapters: $chapter_count"
    info "Ready for indexing: $ready_count"

    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Review metadata: cat $OUTPUT_FILE | jq '.'"
    echo "  2. Submit ready chapters for RAG indexing"
    echo "  3. Update textbook/metadata/module-index.json"
}

main "$@"
