#!/bin/bash

# Find all chapter files and add chapter_id to frontmatter
for file in docs/module-**/chapter-*.md; do
  # Extract chapter number from filename (e.g., chapter-02.md -> 2)
  chap_num=$(echo "$file" | grep -oP 'chapter-\K\d+')
  
  # Skip if chapter_id already exists
  if grep -q "^chapter_id:" "$file"; then
    echo "Skipping $file (already has chapter_id)"
    continue
  fi
  
  # Add chapter_id after sidebar_position
  # First, check if sidebar_position exists
  if grep -q "^sidebar_position:" "$file"; then
    # Add chapter_id after sidebar_position
    sed -i "/^sidebar_position:/a chapter_id: $chap_num" "$file"
    echo "Added chapter_id: $chap_num to $file"
  else
    # If no sidebar_position, add after title
    sed -i "/^title:/a chapter_id: $chap_num" "$file"
    echo "Added chapter_id: $chap_num to $file (after title)"
  fi
done

echo "Done!"
