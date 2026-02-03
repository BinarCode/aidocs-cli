# Documentation Batch Processing Skill

Generate documentation for multiple pages from a list.

## What this skill does:

1. Batch processes multiple URLs or files
2. Generates documentation for all items in the list
3. Handles authentication if needed
4. Organizes output systematically

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/batch/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "batch document these pages"
- "generate docs for all these URLs"
- "document multiple pages at once"
- "batch process this list"

## Arguments:

```
batch <urls-file-or-list>
batch urls.txt --auth user:pass
batch --output ./docs
```

## Input Format:

Can accept:
- File containing URLs (one per line)
- Comma-separated list of URLs
- JSON array of URLs

## Output:

- Documentation for each URL/file
- Summary report
- Progress tracking
- Error reporting for failed items
