#!/bin/bash
#
# validate-references.sh - Reference Validation Script
#
# Purpose: Validates all cited references in chapters against references.json
# Checks: reference existence, APA format, optional URL validation
#
# Usage: ./validate-references.sh [OPTIONS]
#
# Options:
#   -c, --chapter <file>   Validate references in single chapter
#   -a, --all              Validate references in all chapters
#   -u, --check-urls       Validate URLs return 200 OK (optional, slow)
#   -r, --refs <file>      Path to references.json (default: textbook/metadata/references.json)
#   -h, --help             Show this help message
#
# Example:
#   ./validate-references.sh --all
#   ./validate-references.sh --chapter textbook/chapters/01-what-is-humanoid-robotics.md
#   ./validate-references.sh --all --check-urls
#
# Requirements:
#   - jq (JSON processor)
#   - curl (for URL validation, if --check-urls specified)
#   - references.json with APA-formatted references
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
REFS_FILE="$PROJECT_ROOT/textbook/metadata/references.json"
CHECK_URLS=false
VALIDATE_ALL=false
CHAPTER_FILE=""

# Counters
TOTAL_CITATIONS=0
VALID_CITATIONS=0
MISSING_REFS=0
INVALID_FORMAT=0
INVALID_URLS=0

# Help text
show_help() {
    cat << EOF
Reference Validation Script

Purpose: Validates cited references in chapters against references.json

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -c, --chapter <file>    Validate references in single chapter
    -a, --all               Validate references in all chapters
    -u, --check-urls        Validate URLs return 200 OK (optional, slow)
    -r, --refs <file>       Path to references.json (default: textbook/metadata/references.json)

EXAMPLES:
    $0 --all
    $0 --chapter textbook/chapters/01-what-is-humanoid-robotics.md
    $0 --all --check-urls
    $0 --all --refs custom-refs.json

VALIDATION CHECKS:
    1. All cited references exist in references.json
    2. All references follow APA format
    3. (Optional) All URLs return 200 OK

REFERENCE FORMAT:
    references.json should contain array of objects:
    [
      {
        "id": "ref_001",
        "citation": "Author, A. (Year). Title. Publisher.",
        "url": "https://example.com",
        "type": "book|paper|documentation|datasheet"
      }
    ]

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
                VALIDATE_ALL=true
                shift
                ;;
            -u|--check-urls)
                CHECK_URLS=true
                shift
                ;;
            -r|--refs)
                REFS_FILE="$2"
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

    # If --check-urls, check curl is installed
    if [[ "$CHECK_URLS" == true ]] && ! command -v curl &> /dev/null; then
        error "curl is not installed. Required for --check-urls option."
    fi

    # Check if either --all or --chapter specified
    if [[ "$VALIDATE_ALL" == false && -z "$CHAPTER_FILE" ]]; then
        error "Either --all or --chapter must be specified. Use --help for usage."
    fi

    # If single chapter, check it exists
    if [[ -n "$CHAPTER_FILE" && ! -f "$CHAPTER_FILE" ]]; then
        error "Chapter file not found: $CHAPTER_FILE"
    fi

    # Check references.json exists
    if [[ ! -f "$REFS_FILE" ]]; then
        error "References file not found: $REFS_FILE"
    fi

    # Validate references.json is valid JSON
    if ! jq empty "$REFS_FILE" 2>/dev/null; then
        error "References file is not valid JSON: $REFS_FILE"
    fi
}

# Load references into memory
load_references() {
    jq -r '.[] | .id' "$REFS_FILE"
}

# Extract reference IDs from chapter (format: [ref_XXX])
extract_citations() {
    local file="$1"

    # Look for citations in format: [ref_XXX] or (ref_XXX)
    grep -oE '\[(ref_[0-9]{3})\]' "$file" | sed 's/\[//; s/\]//' || true
    grep -oE '\(ref_[0-9]{3}\)' "$file" | sed 's/(//; s/)//' || true
}

# Validate APA format for reference
validate_apa_format() {
    local ref_id="$1"

    # Get citation from references.json
    local citation=$(jq -r ".[] | select(.id == \"$ref_id\") | .citation" "$REFS_FILE")

    if [[ -z "$citation" || "$citation" == "null" ]]; then
        return 1
    fi

    # Basic APA format check: should have Author(s), (Year), Title, and Source
    # Pattern: Author, A. (YYYY). Title. Source.
    if [[ ! "$citation" =~ \([0-9]{4}\) ]]; then
        return 1
    fi

    return 0
}

# Validate URL (if present)
validate_url() {
    local ref_id="$1"

    # Get URL from references.json
    local url=$(jq -r ".[] | select(.id == \"$ref_id\") | .url" "$REFS_FILE")

    if [[ -z "$url" || "$url" == "null" ]]; then
        return 0  # No URL to validate
    fi

    # Check URL returns 200 OK (with timeout)
    if curl --output /dev/null --silent --head --fail --max-time 5 "$url"; then
        return 0
    else
        warn "URL validation failed for $ref_id: $url"
        ((INVALID_URLS++))
        return 1
    fi
}

# Validate references in single chapter
validate_chapter_references() {
    local file="$1"
    local filename=$(basename "$file")

    info "Validating references in: $filename"

    # Load reference IDs
    local valid_refs=$(load_references)

    # Extract citations from chapter
    local citations=$(extract_citations "$file" | sort -u)

    if [[ -z "$citations" ]]; then
        warn "No citations found in $filename"
        return
    fi

    local chapter_citations=0
    local chapter_valid=0
    local chapter_missing=0
    local chapter_invalid_format=0

    while IFS= read -r citation; do
        if [[ -z "$citation" ]]; then
            continue
        fi

        ((chapter_citations++))
        ((TOTAL_CITATIONS++))

        # Check if reference exists in references.json
        if ! echo "$valid_refs" | grep -q "^$citation$"; then
            warn "Missing reference: $citation (cited in $filename)"
            ((chapter_missing++))
            ((MISSING_REFS++))
            continue
        fi

        # Validate APA format
        if ! validate_apa_format "$citation"; then
            warn "Invalid APA format: $citation (in $filename)"
            ((chapter_invalid_format++))
            ((INVALID_FORMAT++))
            continue
        fi

        # Validate URL (if --check-urls specified)
        if [[ "$CHECK_URLS" == true ]]; then
            validate_url "$citation" || true
        fi

        ((chapter_valid++))
        ((VALID_CITATIONS++))

    done <<< "$citations"

    # Chapter summary
    echo "  Citations: $chapter_citations"
    echo "  Valid: $chapter_valid"
    if [[ $chapter_missing -gt 0 ]]; then
        echo -e "  ${RED}Missing: $chapter_missing${NC}"
    fi
    if [[ $chapter_invalid_format -gt 0 ]]; then
        echo -e "  ${YELLOW}Invalid format: $chapter_invalid_format${NC}"
    fi
    echo ""
}

# Validate all chapters
validate_all_chapters() {
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
        return
    fi

    info "Found ${#chapter_files[@]} chapter file(s)"
    echo ""

    # Validate each chapter
    for file in "${chapter_files[@]}"; do
        validate_chapter_references "$file"
    done
}

# Generate validation report
generate_report() {
    echo ""
    echo "========================================"
    echo "REFERENCE VALIDATION REPORT"
    echo "========================================"
    echo ""
    echo "Total citations: $TOTAL_CITATIONS"
    echo -e "Valid citations: ${GREEN}$VALID_CITATIONS${NC}"

    if [[ $MISSING_REFS -gt 0 ]]; then
        echo -e "Missing references: ${RED}$MISSING_REFS${NC}"
    else
        echo -e "Missing references: ${GREEN}0${NC}"
    fi

    if [[ $INVALID_FORMAT -gt 0 ]]; then
        echo -e "Invalid APA format: ${YELLOW}$INVALID_FORMAT${NC}"
    else
        echo -e "Invalid APA format: ${GREEN}0${NC}"
    fi

    if [[ "$CHECK_URLS" == true ]]; then
        if [[ $INVALID_URLS -gt 0 ]]; then
            echo -e "Invalid URLs: ${YELLOW}$INVALID_URLS${NC}"
        else
            echo -e "Invalid URLs: ${GREEN}0${NC}"
        fi
    fi

    echo ""

    # Overall status
    if [[ $MISSING_REFS -eq 0 && $INVALID_FORMAT -eq 0 ]]; then
        echo -e "${GREEN}VALIDATION PASSED${NC}"
        echo "All citations are valid and properly formatted."
        return 0
    else
        echo -e "${RED}VALIDATION FAILED${NC}"
        echo "Please fix missing references and formatting issues."
        return 1
    fi
}

# Main execution
main() {
    parse_args "$@"
    validate_inputs

    info "Starting reference validation..."
    if [[ "$CHECK_URLS" == true ]]; then
        info "URL validation enabled (this may take a while)"
    fi
    echo ""

    # Validate chapters
    if [[ "$VALIDATE_ALL" == true ]]; then
        validate_all_chapters
    else
        validate_chapter_references "$CHAPTER_FILE"
    fi

    # Generate report
    generate_report
    exit_code=$?

    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    if [[ $exit_code -eq 0 ]]; then
        echo "  1. All references validated successfully"
        echo "  2. Ready for expert review submission"
    else
        echo "  1. Add missing references to $REFS_FILE"
        echo "  2. Fix APA format issues"
        echo "  3. Re-run validation: $0 --all"
    fi

    exit $exit_code
}

main "$@"
