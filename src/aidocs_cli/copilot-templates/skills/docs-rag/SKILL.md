---
name: docs:rag
description: |
  # Documentation RAG Query Skill
  
  Setup and query documentation using RAG (Retrieval-Augmented Generation).
  
  ## What this skill does:
  
  1. Complete RAG setup in one command
  2. Chunks documentation
  3. Creates migration if needed
  4. Generates embeddings
tags: [documentation]
---

# Documentation RAG Query Skill

Setup and query documentation using RAG (Retrieval-Augmented Generation).

## What this skill does:

1. Complete RAG setup in one command
2. Chunks documentation
3. Creates migration if needed
4. Generates embeddings
5. Enables semantic documentation search

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/rag/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "setup RAG for documentation"
- "enable semantic doc search"
- "query the documentation"
- "search docs with RAG"

## Arguments:

```
rag
rag --force
rag --skip-migration
```

## Options:

- `--force` - Force regeneration of all embeddings
- `--skip-migration` - Skip migration creation/running

## Process:

1. Checks if migration exists, creates if needed
2. Runs migration
3. Chunks all documentation
4. Generates embeddings
5. Populates vector database
6. Enables semantic search

## Benefits:

- Semantic documentation search
- Find related documentation
- Answer questions from docs
- Intelligent documentation retrieval
