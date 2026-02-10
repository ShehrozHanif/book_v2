#!/usr/bin/env python3
"""
Fix MDX parsing issues in chapter files - improved version.
More conservative approach: only fix what's actually breaking.
"""

import re
from pathlib import Path

DOCS_DIR = Path(r"C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs")

def fix_mdx_issues(content):
    """Fix MDX parsing issues conservatively."""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False

    for line in lines:
        # Track code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            fixed_lines.append(line)
            continue

        # Skip if in code block
        if in_code_block:
            fixed_lines.append(line)
            continue

        # Fix angle brackets that trigger JSX parsing
        # Only fix outside of inline code (backticks)
        if ('<' in line or '>' in line) and '`' not in line:
            # Direct replacement for common problematic patterns
            line = re.sub(r'<(\d)', r'&lt;\1', line)
            line = re.sub(r'>(\d)', r'&gt;\1', line)
            line = re.sub(r'<(\$)', r'&lt;\1', line)
            line = re.sub(r'>(\$)', r'&gt;\1', line)
            line = re.sub(r'<([A-Z])', r'&lt;\1', line)
            line = re.sub(r'>([A-Z])', r'&gt;\1', line)
            line = re.sub(r'<(°)', r'&lt;\1', line)
            line = re.sub(r'>(°)', r'&gt;\1', line)
        elif '<' in line or '>' in line:
            # Split by backticks to preserve inline code
            parts = line.split('`')
            for i in range(0, len(parts), 2):  # Only process non-code parts
                parts[i] = re.sub(r'<(\d)', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>(\d)', r'&gt;\1', parts[i])
                parts[i] = re.sub(r'<(\$)', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>(\$)', r'&gt;\1', parts[i])
                parts[i] = re.sub(r'<([A-Z])', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>([A-Z])', r'&gt;\1', parts[i])
                parts[i] = re.sub(r'<(°)', r'&lt;\1', parts[i])
                parts[i] = re.sub(r'>(°)', r'&gt;\1', parts[i])
            line = '`'.join(parts)

        # DON'T escape curly braces - they're usually fine in markdown
        # Only would be a problem in actual JSX expressions

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
    print("Fixing MDX issues in chapter files (v2 - conservative)...")

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
