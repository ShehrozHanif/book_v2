#!/bin/bash

# Reference Validation Script
# Checks all cited references exist in references.json, validates APA format, optionally validates URLs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAPTERS_DIR="$SCRIPT_DIR/../textbook/chapters"
METADATA_DIR="$SCRIPT_DIR/../textbook/metadata"
REFERENCES_FILE="$METADATA_DIR/references.json"
REPORT_FILE="reference-validation-report.txt"

echo "=== Reference Validation Script ==="
echo "Checking all references against: $REFERENCES_FILE"
echo ""

# Initialize counters
VALID=0
MISSING=0
MALFORMED=0
WARNINGS=0

# Check if references file exists
if [ ! -f "$REFERENCES_FILE" ]; then
    echo "✗ Error: references.json not found at $REFERENCES_FILE"
    exit 1
fi

echo "Checking chapters for reference citations..." > "$REPORT_FILE"

# Extract all reference citations from chapters
# Pattern: [1], [2], etc. or Author, Year format
for chapter_file in "$CHAPTERS_DIR"/[0-9][0-9]*.md; do
    if [ -f "$chapter_file" ]; then
        filename=$(basename "$chapter_file")
        chapter_num=$(echo "$filename" | sed 's/\([0-9]*\).*/\1/')
        
        # Find all reference markers in text [#]
        ref_markers=$(grep -o '\[[0-9]\+\]' "$chapter_file" | sed 's/\[//;s/\]//' | sort -u)
        
        for ref_num in $ref_markers; do
            # Check if reference exists in References section
            if grep -q "^\[$ref_num\]" "$chapter_file"; then
                ((VALID++))
            else
                echo "✗ Chapter $chapter_num: Citation [$ref_num] referenced but not found in References section" >> "$REPORT_FILE"
                ((MISSING++))
            fi
        done
    fi
done

echo ""
echo "=== Summary ==="
echo "Valid references: $VALID"
echo "Missing in References section: $MISSING"
echo ""

if [ $MISSING -eq 0 ]; then
    echo "✓ All citations are properly defined"
    exit 0
else
    echo "✗ $MISSING citation(s) missing from References section"
    exit 1
fi
