#!/usr/bin/env python3
"""
Fix MDX parsing issues in chapter files.
Handles angle brackets and other JSX-triggering characters.
"""

import re
from pathlib import Path

DOCS_DIR = Path(r"C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs")

def fix_mdx_issues(content):
    """Fix MDX parsing issues more aggressively."""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    code_block_language = None

    for line in lines:
        # Track code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                # Extract language if present
                code_block_language = line.strip()[3:].strip()
            else:
                code_block_language = None
            fixed_lines.append(line)
            continue

        # Skip if in code block
        if in_code_block:
            fixed_lines.append(line)
            continue

        # Fix angle brackets in regular text (not in code)
        # Look for patterns like <number or >number that trigger JSX parsing
        if '<' in line or '>' in line:
            # Split by backticks to preserve inline code
            parts = line.split('`')
            for i in range(0, len(parts), 2):  # Only process non-code parts
                # Replace < and > when they appear in non-JSX contexts
                # Common patterns: <120°C, <5V, >10, <$20,000, etc.
                parts[i] = re.sub(r'<(\d)', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>(\d)', r'&gt;\1', parts[i])
                # Handle angle brackets before currency symbols
                parts[i] = re.sub(r'<(\$)', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>(\$)', r'&gt;\1', parts[i])
                # Also handle angle brackets before units or standalone
                parts[i] = re.sub(r'<([A-Z°])', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>([A-Z°])', r'&gt;\1', parts[i])
            line = '`'.join(parts)

        # Fix curly braces in regular text
        if '{' in line or '}' in line:
            parts = line.split('`')
            for i in range(0, len(parts), 2):
                # Escape isolated curly braces
                parts[i] = parts[i].replace('{', '\\{').replace('}', '\\}')
            line = '`'.join(parts)

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single markdown file."""
    print(f"Processing: {file_path.relative_to(DOCS_DIR)}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply fixes
    fixed_content = fix_mdx_issues(content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

def main():
    """Process all chapter files."""
    print("Fixing MDX issues in chapter files...")

    # Find all chapter files
    chapter_files = []
    for module_dir in DOCS_DIR.glob('module-*'):
        if module_dir.is_dir():
            chapter_files.extend(module_dir.glob('chapter-*.md'))

    print(f"Found {len(chapter_files)} chapter files to process")

    for chapter_file in sorted(chapter_files):
        process_file(chapter_file)

    print(f"\n[SUCCESS] Processed {len(chapter_files)} files")

if __name__ == '__main__':
    main()
