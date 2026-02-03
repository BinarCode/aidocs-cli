# Documentation RAG Vectors Skill

Generate embeddings and manage vectors for documentation search.

## What this skill does:

1. Chunks documentation into optimal sizes
2. Generates embeddings using AI models
3. Creates SQL for syncing to vector database
4. Manages vector updates and refreshes

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/rag-vectors/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Prerequisites:

Requires `/docs:rag-init` to be completed first.

## Usage Patterns:

The user might say:
- "generate documentation embeddings"
- "create vectors for docs"
- "update documentation vectors"
- "sync docs to vector database"

## Process:

1. Reads all markdown documentation
2. Chunks content intelligently
3. Generates embeddings
4. Creates SQL insert statements
5. Handles updates to existing vectors

## Output:

- SQL file with vector inserts
- Embedding metadata
- Statistics on processed documents
- Sync status report
