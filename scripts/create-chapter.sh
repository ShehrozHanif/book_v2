#!/bin/bash
set -e

# Chapter Creation Workflow Automation Script
# Usage: ./create-chapter.sh <chapter_number> <module_number> <title>
# Example: ./create-chapter.sh 1 1 "What is a Humanoid Robot?"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <chapter_number> <module_number> <title>"
    echo "Example: $0 1 1 'What is a Humanoid Robot?'"
    exit 1
fi

CHAPTER_NUM=$1
MODULE_NUM=$2
TITLE=$3

# Validate inputs
if ! [[ "$CHAPTER_NUM" =~ ^[0-9]{1,2}$ ]]; then
    echo "Error: Chapter number must be a positive integer"
    exit 1
fi

if ! [[ "$MODULE_NUM" =~ ^[1-4]$ ]]; then
    echo "Error: Module number must be 1-4"
    exit 1
fi

if [ -z "$TITLE" ]; then
    echo "Error: Title cannot be empty"
    exit 1
fi

# Format chapter number with leading zero if needed
CHAPTER_NUM_PADDED=$(printf "%02d" $CHAPTER_NUM)

# Create filename
FILENAME="${CHAPTER_NUM_PADDED}-${TITLE,,}" # Convert to lowercase
FILENAME="${FILENAME// /-}" # Replace spaces with hyphens
FILENAME="${FILENAME/[^a-z0-9-]/}" # Remove special characters
FILENAME="${FILENAME%.md}.md" # Add .md extension
FILEPATH="../textbook/chapters/$FILENAME"

echo "=== Creating Chapter ===" 
echo "Chapter: $CHAPTER_NUM (Module $MODULE_NUM)"
echo "Title: $TITLE"
echo "File: $FILEPATH"
echo ""

# Check if file already exists
if [ -f "$FILEPATH" ]; then
    echo "Warning: File $FILEPATH already exists!"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Create chapter from template
cat > "$FILEPATH" << CHAPTER
---
chapter_id: "$CHAPTER_NUM"
module: "Module $MODULE_NUM"
title: "$TITLE"
word_count_target: 2300
word_count_actual: 0
status: "in_progress"
code_examples: []
references: []
last_updated: "$(date +%Y-%m-%d)"
author: ""
---

# Chapter $CHAPTER_NUM: $TITLE

## Learning Objectives

By the end of this chapter, you will be able to:
- Objective 1
- Objective 2
- Objective 3

## Introduction

[Introduction paragraph providing context and motivation for the chapter content]

## Section 1: [Topic]

[Content for section 1]

### Code Example 1: [Example Title]

[Brief description of what this example demonstrates]

\`\`\`python
# Code example demonstrating [concept]
# Run with: python filename.py
# Expected output: [describe expected output]

def example_function():
    pass
\`\`\`

## Section 2: [Topic]

[Content for section 2]

### Code Example 2: [Example Title]

[Brief description of what this example demonstrates]

\`\`\`python
# Code example demonstrating [concept]
# Run with: python filename.py
# Expected output: [describe expected output]

def another_example():
    pass
\`\`\`

## Section 3: [Topic]

[Content for section 3]

## Key Concepts Summary

- **Concept 1**: Brief definition
- **Concept 2**: Brief definition
- **Concept 3**: Brief definition

## References

[1] Author, A. (Year). *Title of publication*. Publisher. https://doi.org/xxx

[2] Author, B. (Year). *Title of publication*. Publisher. https://doi.org/xxx

## Further Reading

- [Recommended resource 1]
- [Recommended resource 2]

## Exercises

1. [Exercise 1 prompt]
2. [Exercise 2 prompt]
3. [Exercise 3 prompt]

---

**Status**: in_progress
**Last Updated**: $(date +%Y-%m-%d)
**Author Notes**: [Any notes for reviewers or future editors]
CHAPTER

echo "✓ Chapter created: $FILEPATH"
echo ""
echo "Next steps:"
echo "1. Edit the chapter file to add content"
echo "2. Create code examples in textbook/code-examples/"
echo "3. Update references in textbook/metadata/references.json"
echo "4. Run: bash verify-word-count.sh"
echo "5. Run: bash test-code-examples.sh"
echo "6. Run: bash validate-references.sh"
