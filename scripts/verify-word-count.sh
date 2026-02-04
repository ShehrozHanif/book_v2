#!/bin/bash

# Chapter Word Count Verification Script
# Validates that each chapter is within ±10% of target word count (2300-2400 words)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAPTERS_DIR="$SCRIPT_DIR/../textbook/chapters"
REPORT_FILE="word-count-report.txt"

TARGET_MIN=2070  # 2300 - 10%
TARGET_MAX=2530  # 2300 + 10%
TOTAL_TARGET=52000  # All 22 chapters

echo "=== Chapter Word Count Verification ==="
echo "Target per chapter: 2,300-2,400 words (±10%)"
echo "Minimum: $TARGET_MIN, Maximum: $TARGET_MAX"
echo ""

# Initialize variables
TOTAL_WORDS=0
PASS=0
FAIL=0
WARNING=0

# Create report header
echo "Word Count Verification Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "Target per chapter: $TARGET_MIN - $TARGET_MAX words" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Checking chapters..." > /dev/tty

# Check each chapter file (excluding template)
for chapter_file in "$CHAPTERS_DIR"/[0-9][0-9]*.md; do
    if [ -f "$chapter_file" ]; then
        filename=$(basename "$chapter_file")
        
        # Count words (excluding YAML front matter)
        word_count=$(sed '/^---$/,/^---$/d' "$chapter_file" | wc -w)
        
        # Extract chapter number and title
        chapter_num=$(echo "$filename" | sed 's/\([0-9]*\).*/\1/')
        chapter_title=$(sed -n 's/^# Chapter [0-9]*: //p' "$chapter_file" | head -1)
        
        TOTAL_WORDS=$((TOTAL_WORDS + word_count))
        
        # Check if within target range
        if [ "$word_count" -lt "$TARGET_MIN" ]; then
            status="✗ BELOW TARGET"
            ((FAIL++))
        elif [ "$word_count" -gt "$TARGET_MAX" ]; then
            status="✗ ABOVE TARGET"
            ((FAIL++))
        else
            status="✓ OK"
            ((PASS++))
        fi
        
        # Print result
        printf "Chapter %02d: %5d words %s\n" "$chapter_num" "$word_count" "$status"
        echo "Chapter $chapter_num: $word_count words | $chapter_title" >> "$REPORT_FILE"
    fi
done

echo "" | tee -a "$REPORT_FILE"
echo "=== Summary ===" | tee -a "$REPORT_FILE"
echo "Chapters checked: $((PASS + FAIL))" | tee -a "$REPORT_FILE"
echo "Within target: $PASS" | tee -a "$REPORT_FILE"
echo "Outside target: $FAIL" | tee -a "$REPORT_FILE"
echo "Total words: $TOTAL_WORDS" | tee -a "$REPORT_FILE"
echo "Target total: $TOTAL_TARGET" | tee -a "$REPORT_FILE"

if [ $FAIL -eq 0 ]; then
    echo "✓ All chapters within target range" | tee -a "$REPORT_FILE"
    exit 0
else
    echo "✗ $FAIL chapter(s) outside target range" | tee -a "$REPORT_FILE"
    exit 1
fi
