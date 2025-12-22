---
name: docs:sync
description: Generate embeddings and SQL for syncing docs to vector DB
---

# Sync Documentation to Vector DB

Generate embeddings and SQL script for importing documentation chunks to PostgreSQL.

**Usage:**
```
/docs:sync                    # Generate sync SQL
/docs:sync --dry              # Preview what would be synced
/docs:sync --force            # Re-sync all (ignore last-sync)
```

**Prerequisites:**
- Run `aidocs chunk` first to create .chunks.json files
- Set `OPENAI_API_KEY` environment variable

**What it does:**
1. Reads `docs/.chunks/manifest.json` for chunk file locations
2. Compares against `docs/.chunks/last-sync.json` to find changes
3. Generates embeddings via OpenAI API (only for new/changed chunks)
4. Creates `docs/.chunks/sync.sql` with INSERT statements

**Output:**
```
📊 Sync Analysis:
   Unchanged: 12 files (skipped)
   Changed: 2 files (8 chunks)
   New: 1 file (3 chunks)

📄 Generated: docs/.chunks/sync.sql

Run with:
   psql $DATABASE_URL -f docs/.chunks/sync.sql
```

---

**Execute workflow:** `@.claude/workflows/docs/sync/workflow.md`
