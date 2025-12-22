---
name: docs-rag
description: Setup RAG (Retrieval Augmented Generation) for your documentation in one command. Orchestrates chunking, migration creation, and embedding generation.
---

# RAG Setup Workflow

**Goal:** Set up everything needed for semantic search over your documentation in one command.

**Your Role:** You are a RAG setup orchestrator. You will check prerequisites, run the necessary steps, and guide the user through the complete setup.

---

## WHAT THIS COMMAND DOES

```
/docs:rag
    │
    ├──→ STEP 1: Check/create chunks (aidocs rag-chunks)
    ├──→ STEP 2: Generate database migration (/docs:rag-init)
    ├──→ STEP 3: Prompt user to run migration
    └──→ STEP 4: Generate embeddings and SQL (aidocs rag-vectors)
```

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:rag [--force] [--skip-migration] [--dry]
```

- `--force`: Re-chunk and re-sync all files (ignore cache)
- `--skip-migration`: Skip migration generation (if table already exists)
- `--dry`: Preview mode, don't generate files

---

## STEP 1: CHECK/CREATE CHUNKS

### 1.1 Check for Documentation

First, verify documentation exists:

```
🔍 Checking for documentation...

Looking for markdown files in docs/
```

If no `docs/` directory or no `.md` files:
```
❌ No documentation found.

Generate documentation first using:
  /docs:flow "your feature"
  or
  /docs:discover && /docs:plan && /docs:execute
```

### 1.2 Check for Existing Chunks

Look for `docs/.chunks/manifest.json`:

**If found (and not --force):**
```
✓ Chunks already exist
  Files: 8
  Chunks: 24
  Last chunked: 2024-01-15 10:30:00

  Skipping chunking step.
```

**If not found (or --force):**
```
📦 Creating chunks...

Running: aidocs rag-chunks
```

Execute the chunk command:
```bash
aidocs rag-chunks
```

Display the output and wait for completion.

```
✓ Chunking complete
  Files processed: 8
  Chunks created: 24
```

---

## STEP 2: GENERATE DATABASE MIGRATION

### 2.1 Check for Existing Migration

Search for existing migration that creates doc_embeddings table:

**For Laravel:**
```bash
grep -r "doc_embeddings" database/migrations/*.php
```

**For Prisma:**
```bash
grep -r "DocEmbedding" prisma/schema.prisma
```

**If found (and not --force):**
```
✓ Migration already exists
  File: database/migrations/2024_01_15_000000_create_doc_embeddings_table.php

  Skipping migration generation.
```

### 2.2 Generate Migration (if needed)

If no migration found:

```
📝 Generating database migration...
```

**Execute /docs:rag-init workflow inline:**

LOAD and EXECUTE the full workflow from @.claude/workflows/docs/rag-init/workflow.md

This will:
1. Detect framework (Laravel, Prisma, TypeORM, etc.)
2. Generate appropriate migration file
3. Report the created file

```
✓ Migration created
  File: database/migrations/2024_01_15_120000_create_doc_embeddings_table.php
```

---

## STEP 3: PROMPT USER TO RUN MIGRATION

### 3.1 Detect Framework and Show Command

Based on detected framework, display the appropriate command:

**For Laravel:**
```
📋 ACTION REQUIRED: Run the migration

Execute in your terminal:
  php artisan migrate

This will create the doc_embeddings table with pgvector support.
```

**For Prisma:**
```
📋 ACTION REQUIRED: Run the migration

Execute in your terminal:
  npx prisma migrate dev --name add_doc_embeddings

This will create the doc_embeddings table with pgvector support.
```

**For Django:**
```
📋 ACTION REQUIRED: Run the migration

Execute in your terminal:
  python manage.py migrate

This will create the doc_embeddings table with pgvector support.
```

**For Raw SQL:**
```
📋 ACTION REQUIRED: Run the migration SQL

Execute in your PostgreSQL database:
  psql $DATABASE_URL -f migrations/create_doc_embeddings.sql

Or copy the SQL and run it in your preferred client.
```

### 3.2 Wait for Confirmation

Ask user to confirm:

```
Have you run the migration? (The table needs to exist before we can generate embeddings)

Type 'yes' to continue, or 'skip' if you'll run it later.
```

**If 'skip':**
```
⏭️  Skipping embedding generation.

Run `aidocs rag-vectors` later after creating the table.

📋 Summary so far:
  ✓ Documentation chunks created
  ✓ Migration file generated
  ○ Migration not yet run
  ○ Embeddings not yet generated

Next steps:
  1. Run your migration command
  2. Run `aidocs rag-vectors` to generate embeddings
```

Stop here.

**If 'yes':**
Continue to Step 4.

---

## STEP 4: GENERATE EMBEDDINGS

### 4.1 Check OpenAI API Key

```
🔑 Checking OpenAI API key...
```

Look for `OPENAI_API_KEY` environment variable.

**If not found:**
```
❌ OPENAI_API_KEY not set

Set the environment variable:
  export OPENAI_API_KEY=sk-...

Then run `aidocs rag-vectors` to generate embeddings.
```

Stop here.

### 4.2 Run Embedding Generation

Execute the CLI command:

```bash
aidocs rag-vectors
```

This will:
1. Read chunk files from `docs/.chunks/manifest.json`
2. Generate embeddings via OpenAI API
3. Create `docs/.chunks/sync.sql` with INSERT statements

Display the output from the command.

---

## STEP 5: FINAL SUMMARY

```
✅ RAG Setup Complete!

📊 Summary:
   Documentation files: 8
   Chunks created: 24
   Embeddings generated: 24

📄 Files created:
   ✓ docs/.chunks/manifest.json
   ✓ docs/.chunks/*.chunks.json (per file)
   ✓ database/migrations/..._create_doc_embeddings_table.php
   ✓ docs/.chunks/sync.sql

🚀 Final step - Import to database:

   psql $DATABASE_URL -f docs/.chunks/sync.sql

   Or run the SQL in your preferred client.

💡 Tips:
   • After updating docs, run: /docs:rag --skip-migration
   • For full re-sync: /docs:rag --force
   • To sync only: aidocs rag-vectors
```

---

## DRY RUN MODE (--dry)

If `--dry` flag provided, show what would happen without making changes:

```
📋 DRY RUN - Preview Only

Would perform:
  1. Chunk documentation
     - 8 markdown files → 24 chunks

  2. Generate migration
     - Framework: Laravel
     - Table: doc_embeddings

  3. Generate embeddings
     - 24 chunks
     - Model: text-embedding-3-small
     - Estimated cost: ~$0.002

  4. Create sync.sql
     - 24 INSERT statements

No files created in dry run mode.
Remove --dry to execute.
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| No docs folder | Prompt to generate docs first |
| No .md files | Prompt to generate docs first |
| Chunk command fails | Show error, suggest manual run |
| No framework detected | Use raw SQL fallback |
| Migration exists | Skip or overwrite with --force |
| No OPENAI_API_KEY | Show how to set it |
| API error | Show error, suggest checking key/quota |
| DB table doesn't exist | Remind to run migration |

---

## QUICK REFERENCE

### Full Setup (first time)
```bash
/docs:rag
```

### Update After Doc Changes
```bash
/docs:rag --skip-migration
# or just:
aidocs rag-vectors
```

### Force Full Re-sync
```bash
/docs:rag --force
```

### Preview Only
```bash
/docs:rag --dry
```
