#!/bin/bash
for file in *.skill.md; do
  name="${file%.skill.md}"
  mkdir -p "$name"
  
  # Add YAML frontmatter and move content
  {
    echo "---"
    echo "name: $name"
    echo "description: |"
    # Extract first few lines as description
    head -10 "$file" | sed 's/^/  /'
    echo "tags: [documentation]"
    echo "---"
    echo ""
    cat "$file"
  } > "$name/SKILL.md"
  
  echo "Created: $name/SKILL.md"
done
