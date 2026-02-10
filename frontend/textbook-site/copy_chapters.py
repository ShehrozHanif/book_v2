#!/usr/bin/env python3
"""
Copy and convert textbook chapters to Docusaurus format.
Handles MDX compatibility and frontmatter conversion.
"""

import os
import re
import shutil
from pathlib import Path

# Define paths
TEXTBOOK_CHAPTERS = Path(r"C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\textbook\chapters")
DOCS_DIR = Path(r"C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site\docs")

# Module mapping
MODULE_MAPPING = {
    "01": "module-01",
    "02": "module-01",
    "03": "module-01",
    "04": "module-01",
    "05": "module-01",
    "06": "module-02",
    "07": "module-02",
    "08": "module-02",
    "09": "module-02",
    "10": "module-02",
    "11": "module-03",
    "12": "module-03",
    "13": "module-03",
    "14": "module-03",
    "15": "module-03",
    "16": "module-04",
    "17": "module-05",
    "18": "module-05",
    "19": "module-05",
    "20": "module-05",
    "21": "module-05",
    "22": "module-05",
}

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        body = content[match.end():]
        return frontmatter, body
    return None, content

def parse_frontmatter(frontmatter_text):
    """Parse YAML frontmatter into dict."""
    data = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"')
    return data

def fix_mdx_issues(content):
    """Fix common MDX parsing issues."""
    # Escape curly braces in text (but not in code blocks)
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

        # Fix standalone curly braces in regular text (not in code or HTML tags)
        # Only escape if they appear outside of backticks
        if '{' in line or '}' in line:
            # Split by backticks to preserve inline code
            parts = line.split('`')
            for i in range(0, len(parts), 2):  # Only process non-code parts
                # Escape isolated curly braces
                parts[i] = parts[i].replace('{', '\\{').replace('}', '\\}')
            line = '`'.join(parts)

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def create_docusaurus_frontmatter(chapter_num, old_frontmatter):
    """Create Docusaurus-compatible frontmatter."""
    data = parse_frontmatter(old_frontmatter)

    title = data.get('title', f'Chapter {chapter_num}')

    # Create slug from chapter number
    slug = f'chapter-{chapter_num}'

    # Create new frontmatter
    new_frontmatter = f"""---
id: {slug}
title: "{title}"
sidebar_label: "Ch {chapter_num}: {title.replace('Chapter ' + chapter_num + ': ', '')}"
sidebar_position: {int(chapter_num)}
---"""

    return new_frontmatter

def process_chapter(chapter_file, output_dir):
    """Process a single chapter file."""
    # Read the file
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Get chapter number from filename
    chapter_num = chapter_file.stem.split('-')[0]

    # Create new frontmatter
    if frontmatter:
        new_frontmatter = create_docusaurus_frontmatter(chapter_num, frontmatter)
    else:
        new_frontmatter = f"""---
id: chapter-{chapter_num}
title: "Chapter {chapter_num}"
sidebar_position: {int(chapter_num)}
---"""

    # Fix MDX issues in body
    body = fix_mdx_issues(body)

    # Combine
    new_content = new_frontmatter + '\n\n' + body

    # Write to output
    output_file = output_dir / f'chapter-{chapter_num}.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Processed: {chapter_file.name} -> {output_file.relative_to(DOCS_DIR)}")
    return chapter_num, new_frontmatter

def main():
    """Main processing function."""
    print("Starting chapter copy and conversion...")

    # Get all chapter files
    chapter_files = sorted([f for f in TEXTBOOK_CHAPTERS.glob('*.md')
                           if f.name[0].isdigit()])

    print(f"Found {len(chapter_files)} chapter files")

    processed = []

    for chapter_file in chapter_files:
        # Get chapter number (first two digits)
        chapter_num = chapter_file.name[:2]

        # Determine target module
        if chapter_num in MODULE_MAPPING:
            module = MODULE_MAPPING[chapter_num]
            output_dir = DOCS_DIR / module

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process the chapter
            chapter_num, frontmatter = process_chapter(chapter_file, output_dir)
            processed.append((chapter_num, module))
        else:
            print(f"Warning: No module mapping for chapter {chapter_num}")

    print(f"\n[SUCCESS] Successfully processed {len(processed)} chapters")

    # Print summary
    print("\nChapter Distribution:")
    for module in sorted(set(MODULE_MAPPING.values())):
        chapters = [c for c, m in processed if m == module]
        print(f"  {module}: Chapters {', '.join(sorted(chapters))}")

    return processed

if __name__ == '__main__':
    processed = main()
