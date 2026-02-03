# Documentation RAG Initialization Skill

Initialize RAG (Retrieval-Augmented Generation) system for documentation.

## What this skill does:

1. Generates database migration for documentation embeddings
2. Sets up pgvector extension
3. Detects framework (Laravel, Prisma, TypeORM, etc.)
4. Creates appropriate migration files

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/rag-init/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "initialize RAG for documentation"
- "setup vector database for docs"
- "create embeddings migration"
- "setup doc search with RAG"

## Arguments:

```
rag-init
rag-init --dimensions 1536
rag-init --dimensions 3072
```

## What it creates:

For Laravel:
- Migration file in `database/migrations/`
- Pgvector extension setup
- Documentation embeddings table

For other frameworks:
- Framework-specific migration
- Vector column configuration
- Index setup

## Next Steps:

After initialization:
1. Run the migration
2. Use `/docs:rag-vectors` to generate embeddings
3. Use `/docs:rag` for semantic documentation search
