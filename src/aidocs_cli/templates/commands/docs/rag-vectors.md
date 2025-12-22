---
name: docs:rag-vectors
description: Generate embeddings and SQL for syncing docs to vector DB
---

# Generate Documentation Embeddings

Generate embeddings and SQL script for importing documentation chunks to PostgreSQL.

**Usage:**
```bash
aidocs rag-vectors                    # Generate sync SQL
aidocs rag-vectors --dry              # Preview what would be synced
aidocs rag-vectors --force            # Re-sync all (ignore last-sync)
aidocs rag-vectors --table my_docs    # Custom table name
```

**Prerequisites:**
- Run `aidocs rag-chunks` first to create .chunks.json files
- Set `OPENAI_API_KEY` environment variable

**What it does:**
1. Reads `docs/.chunks/manifest.json` for chunk file locations
2. Compares against `docs/.chunks/last-sync.json` to find changes
3. Generates embeddings via OpenAI API (only for new/changed chunks)
4. Creates `docs/.chunks/sync.sql` with INSERT statements

**Output:**
```
📊 Sync Summary:
   Unchanged: 12 files (skipped)
   Changed: 2 files (8 chunks)
   New: 1 file (3 chunks)

📄 Generated: docs/.chunks/sync.sql

Run with:
   psql $DATABASE_URL -f docs/.chunks/sync.sql
```

---

**Run the CLI command:**
```bash
aidocs rag-vectors
```
