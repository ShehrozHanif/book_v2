#!/bin/bash

# create-chapter.sh - Chapter Writing Workflow Automation Script
# Purpose: Auto-generate chapter file from template with metadata headers
# Usage: ./create-chapter.sh --id <chapter_id> --module <module> --title <title>

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_PATH="$PROJECT_ROOT/textbook/chapters/_chapter-template.md"
OUTPUT_DIR="$PROJECT_ROOT/textbook/chapters"
CHAPTER_ID=""
MODULE=""
TITLE=""
AUTHOR="${USER:-Unknown}"
WORD_COUNT_TARGET=2300

# Help text
show_help() {
    cat << EOF
Chapter Writing Workflow Automation Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -i, --id <id>          Chapter ID (e.g., 01, 02, ..., 22) [REQUIRED]
    -m, --module <module>  Module name (e.g., "Module 1", "Module 2") [REQUIRED]
    -t, --title <title>    Chapter title [REQUIRED]
    -a, --author <author>  Author name (default: $AUTHOR)
    -w, --words <count>    Word count target (default: $WORD_COUNT_TARGET)

EXAMPLES:
    $0 --id 01 --module "Module 1" --title "What is a Humanoid Robot?"
    $0 -i 06 -m "Module 2" -t "ROS 2 Fundamentals" -a "John Doe" -w 2400

OUTPUT:
    Creates a new chapter file at: textbook/chapters/<id>-<slug>.md
    File is initialized with metadata headers and template structure

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
            -i|--id)
                CHAPTER_ID="$2"
                shift 2
                ;;
            -m|--module)
                MODULE="$2"
                shift 2
                ;;
            -t|--title)
                TITLE="$2"
                shift 2
                ;;
            -a|--author)
                AUTHOR="$2"
                shift 2
                ;;
            -w|--words)
                WORD_COUNT_TARGET="$2"
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
    if [[ -z "$CHAPTER_ID" ]]; then
        error "Chapter ID is required. Use --id <id>"
    fi

    if [[ -z "$MODULE" ]]; then
        error "Module name is required. Use --module <module>"
    fi

    if [[ -z "$TITLE" ]]; then
        error "Chapter title is required. Use --title <title>"
    fi

    # Validate chapter ID format (should be 01-22)
    if ! [[ "$CHAPTER_ID" =~ ^[0-9]{2}$ ]]; then
        error "Chapter ID must be a two-digit number (01-22)"
    fi

    # Check if template exists
    if [[ ! -f "$TEMPLATE_PATH" ]]; then
        error "Chapter template not found at: $TEMPLATE_PATH"
    fi

    # Create output directory if it doesn't exist
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        warn "Output directory not found. Creating: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
    fi
}

# Create slug from title
create_slug() {
    local title="$1"
    # Convert to lowercase, replace spaces with hyphens, remove special characters
    echo "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 -]//g' | sed 's/ \+/-/g'
}

# Generate chapter file
generate_chapter() {
    local slug=$(create_slug "$TITLE")
    local output_file="$OUTPUT_DIR/${CHAPTER_ID}-${slug}.md"
    local current_date=$(date +%Y-%m-%d)

    # Check if file already exists
    if [[ -f "$output_file" ]]; then
        error "Chapter file already exists: $output_file"
    fi

    info "Generating chapter file: $output_file"

    # Read template and replace placeholders
    cp "$TEMPLATE_PATH" "$output_file"

    # Replace metadata placeholders
    sed -i "s/chapter_id: \"XX\"/chapter_id: \"$CHAPTER_ID\"/" "$output_file"
    sed -i "s/module: \"Module N\"/module: \"$MODULE\"/" "$output_file"
    sed -i "s/title: \"Chapter Title\"/title: \"$TITLE\"/" "$output_file"
    sed -i "s/word_count_target: 2300/word_count_target: $WORD_COUNT_TARGET/" "$output_file"
    sed -i "s/author: \"\"/author: \"$AUTHOR\"/" "$output_file"
    sed -i "s/last_updated: \"\"/last_updated: \"$current_date\"/" "$output_file"

    # Replace title in body
    sed -i "s/# Chapter Title/# $TITLE/" "$output_file"

    # Initialize code examples array (empty for now)
    sed -i "s/code_examples: \[\]/code_examples: []/" "$output_file"

    info "Chapter file created successfully!"
    info "File path: $output_file"
    info "Chapter ID: $CHAPTER_ID"
    info "Module: $MODULE"
    info "Title: $TITLE"
    info "Author: $AUTHOR"
    info "Word count target: $WORD_COUNT_TARGET"
    info "Last updated: $current_date"

    echo ""
    info "Next steps:"
    echo "  1. Edit the chapter file: $output_file"
    echo "  2. Fill in learning objectives, sections, and content"
    echo "  3. Add code examples"
    echo "  4. Verify word count: ./scripts/verify-word-count.sh --file $output_file"
    echo "  5. Test code examples: ./scripts/test-code-examples.sh"
    echo "  6. Submit for review"
}

# Main execution
main() {
    parse_args "$@"
    validate_inputs
    generate_chapter
}

main "$@"
