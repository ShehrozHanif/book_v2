#!/bin/bash

# verify-word-count.sh - Chapter Word Count Verification Script
# Purpose: Count words in chapter markdown files and validate against targets
# Validates within ±10% of target (2300-2400 words per chapter)

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHAPTERS_DIR="$PROJECT_ROOT/textbook/chapters"

# Flags
VERBOSE=false
FILE_MODE=false
TARGET_FILE=""
TOLERANCE=10  # Percentage tolerance (±10%)

# Counters
TOTAL_CHAPTERS=0
COMPLIANT_CHAPTERS=0
NON_COMPLIANT_CHAPTERS=0

# Help text
show_help() {
    cat << EOF
Chapter Word Count Verification Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Verbose output with detailed statistics
    -f, --file <file>       Verify specific chapter file
    -t, --tolerance <pct>   Tolerance percentage (default: 10%)

VALIDATION RULES:
    - Excludes YAML frontmatter (between --- markers)
    - Excludes code blocks (between ``` markers)
    - Excludes inline code (between backticks)
    - Excludes markdown headers (#, ##, etc.)
    - Counts only body text words
    - Target range: ±10% of target (e.g., 2300 ± 230 = 2070-2530)

EXAMPLES:
    $0                                  # Verify all chapters
    $0 --verbose                        # Detailed statistics
    $0 --file textbook/chapters/01-*.md # Verify specific chapter
    $0 --tolerance 15                   # Use ±15% tolerance

OUTPUT:
    Generates chapter-by-chapter breakdown and summary statistics
    Returns exit code 0 if all chapters compliant, non-zero otherwise

EOF
}

# Error handler
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

# Info handler
info() {
    echo -e "${GREEN}INFO: $1${NC}"
}

# Warning handler
warn() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Debug handler
debug() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}DEBUG: $1${NC}"
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--file)
                FILE_MODE=true
                TARGET_FILE="$2"
                shift 2
                ;;
            -t|--tolerance)
                TOLERANCE="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1. Use --help for usage information."
                exit 1
                ;;
        esac
    done
}

# Count words in markdown file
count_words() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        error "File not found: $file"
        return 1
    fi

    # Create temporary file for processing
    local temp_file=$(mktemp)

    # Remove YAML frontmatter (between --- markers)
    awk '
    BEGIN { in_frontmatter=0; past_frontmatter=0 }
    /^---$/ {
        if (!past_frontmatter) {
            in_frontmatter = !in_frontmatter
            if (!in_frontmatter) past_frontmatter=1
            next
        }
    }
    !in_frontmatter && past_frontmatter { print }
    ' "$file" > "$temp_file"

    # Remove code blocks (between ``` markers)
    awk '
    BEGIN { in_code=0 }
    /^```/ { in_code = !in_code; next }
    !in_code { print }
    ' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"

    # Remove inline code (between backticks)
    sed 's/`[^`]*`//g' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"

    # Remove markdown headers
    sed 's/^#\+\s*//g' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"

    # Remove markdown links but keep text
    sed 's/\[([^]]*)\]([^)]*)/\1/g' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"

    # Remove markdown formatting (bold, italic)
    sed 's/\*\*\([^*]*\)\*\*/\1/g' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"
    sed 's/\*\([^*]*\)\*/\1/g' "$temp_file" > "${temp_file}.2" && mv "${temp_file}.2" "$temp_file"

    # Count words
    local word_count=$(wc -w < "$temp_file" | tr -d ' ')

    # Cleanup
    rm -f "$temp_file"

    echo "$word_count"
}

# Extract target word count from frontmatter
get_target_from_frontmatter() {
    local file="$1"
    local target=$(grep "^word_count_target:" "$file" | head -1 | sed 's/word_count_target:\s*//' | tr -d ' ')

    if [[ -z "$target" ]]; then
        echo "2300"  # Default
    else
        echo "$target"
    fi
}

# Verify single chapter
verify_chapter() {
    local file="$1"
    local filename=$(basename "$file")

    TOTAL_CHAPTERS=$((TOTAL_CHAPTERS + 1))

    # Get target from frontmatter
    local target=$(get_target_from_frontmatter "$file")
    local actual=$(count_words "$file")

    # Calculate tolerance range
    local tolerance_amount=$((target * TOLERANCE / 100))
    local min_words=$((target - tolerance_amount))
    local max_words=$((target + tolerance_amount))

    # Calculate percentage
    local percentage=0
    if [[ $target -gt 0 ]]; then
        percentage=$(( (actual * 100) / target ))
    fi

    local deviation=$(( actual - target ))
    local deviation_pct=0
    if [[ $target -gt 0 ]]; then
        deviation_pct=$(( (deviation * 100) / target ))
    fi

    # Check compliance
    local status="PASS"
    local status_color="$GREEN"
    if [[ $actual -lt $min_words ]] || [[ $actual -gt $max_words ]]; then
        status="FAIL"
        status_color="$RED"
        NON_COMPLIANT_CHAPTERS=$((NON_COMPLIANT_CHAPTERS + 1))
    else
        COMPLIANT_CHAPTERS=$((COMPLIANT_CHAPTERS + 1))
    fi

    # Print result
    printf "%-40s | Target: %4d | Actual: %4d | %s%s%s" \
        "$filename" "$target" "$actual" "$status_color" "$status" "$NC"

    if [[ "$VERBOSE" == true ]]; then
        printf " | Deviation: %+5d (%+3d%%)" "$deviation" "$deviation_pct"
    fi

    printf "\n"

    # Additional details if verbose
    if [[ "$VERBOSE" == true ]]; then
        debug "  Range: $min_words - $max_words words (±$TOLERANCE%)"
        debug "  Percentage of target: $percentage%"
    fi
}

# Verify all chapters
verify_all_chapters() {
    if [[ ! -d "$CHAPTERS_DIR" ]]; then
        error "Chapters directory not found: $CHAPTERS_DIR"
        exit 1
    fi

    info "Starting word count verification..."
    info "Chapters directory: $CHAPTERS_DIR"
    info "Tolerance: ±$TOLERANCE%"
    echo ""

    # Find all chapter files (exclude template)
    local files=()
    mapfile -t files < <(find "$CHAPTERS_DIR" -type f -name "*.md" ! -name "_*" 2>/dev/null | sort)

    if [[ ${#files[@]} -eq 0 ]]; then
        warn "No chapter files found in $CHAPTERS_DIR"
        exit 0
    fi

    info "Found ${#files[@]} chapter file(s)"
    echo ""
    echo "=========================================="
    echo "       WORD COUNT VERIFICATION"
    echo "=========================================="

    # Verify each chapter
    for file in "${files[@]}"; do
        verify_chapter "$file"
    done
}

# Print summary
print_summary() {
    echo ""
    echo "=========================================="
    echo "           SUMMARY STATISTICS"
    echo "=========================================="
    echo -e "Total chapters:       ${BLUE}$TOTAL_CHAPTERS${NC}"
    echo -e "Compliant:            ${GREEN}$COMPLIANT_CHAPTERS${NC}"
    echo -e "Non-compliant:        ${RED}$NON_COMPLIANT_CHAPTERS${NC}"

    if [[ $TOTAL_CHAPTERS -gt 0 ]]; then
        local compliance_pct=$(( (COMPLIANT_CHAPTERS * 100) / TOTAL_CHAPTERS ))
        echo -e "Compliance rate:      ${BLUE}$compliance_pct%${NC}"
    fi

    echo "=========================================="

    if [[ $NON_COMPLIANT_CHAPTERS -eq 0 ]]; then
        echo -e "${GREEN}✓ All chapters within target range!${NC}"
        return 0
    else
        echo -e "${RED}✗ Some chapters outside target range${NC}"
        return 1
    fi
}

# Main execution
main() {
    parse_args "$@"

    if [[ "$FILE_MODE" == true ]]; then
        # Verify single file
        if [[ ! -f "$TARGET_FILE" ]]; then
            error "File not found: $TARGET_FILE"
            exit 1
        fi
        info "Verifying single file: $TARGET_FILE"
        echo ""
        verify_chapter "$TARGET_FILE"
        echo ""
        print_summary
    else
        # Verify all chapters
        verify_all_chapters
        print_summary
    fi
}

main "$@"
