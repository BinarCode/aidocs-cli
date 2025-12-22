---
name: docs-vector-init
description: Generate database migration for documentation embeddings with pgvector. Detects project framework and creates appropriate migration file.
---

# Vector Database Initialization Workflow

**Goal:** Create a database migration for storing documentation embeddings using PostgreSQL with pgvector.

**Your Role:** You are a database migration generator. You will detect the project's framework/ORM and generate the appropriate migration file for storing document embeddings.

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:vector-init [--dimensions 1536|3072] [--table doc_embeddings]
```

- `--dimensions`: Vector dimensions (default: 1536 for text-embedding-3-small)
- `--table`: Table name (default: doc_embeddings)

**Default values:**
- dimensions: `1536`
- table: `doc_embeddings`

---

## STEP 1: DETECT FRAMEWORK

Analyze the project to determine which framework/ORM is being used.

### 1.1 Check for Laravel

Look for these indicators:
- `composer.json` exists AND contains `"laravel/framework"`
- `artisan` file exists in root

```bash
# Check composer.json
cat composer.json | grep -q "laravel/framework"

# Check for artisan
test -f artisan
```

**If Laravel detected → Use Laravel Migration Template**

### 1.2 Check for Node.js ORMs

Look in `package.json` for:
- `prisma` or `@prisma/client` → **Prisma**
- `typeorm` → **TypeORM**
- `drizzle-orm` → **Drizzle**
- `sequelize` → **Sequelize**
- `knex` → **Knex**

```bash
# Check package.json for ORMs
cat package.json | grep -E "(prisma|typeorm|drizzle-orm|sequelize|knex)"
```

### 1.3 Check for Django

Look for:
- `manage.py` exists
- `settings.py` exists somewhere

```bash
# Check for Django
test -f manage.py && find . -name "settings.py" -path "*/settings.py" | head -1
```

### 1.4 Fallback

If no framework detected, generate raw PostgreSQL SQL.

---

## STEP 2: DISPLAY DETECTION RESULT

```
🔍 Framework Detection

Detected: {Laravel 11 / Prisma / TypeORM / etc. / None}
Database: PostgreSQL (required for pgvector)
Embedding dimensions: {dimensions}
Table name: {table}

Proceeding to generate migration...
```

---

## STEP 3: GENERATE MIGRATION

Based on detected framework, generate the appropriate migration.

---

### TEMPLATE: LARAVEL

**Create file:** `database/migrations/{YYYY_MM_DD_HHMMSS}_create_doc_embeddings_table.php`

Use current timestamp for the filename prefix.

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        // Enable pgvector extension
        DB::statement('CREATE EXTENSION IF NOT EXISTS vector');

        Schema::create('{table}', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('file_path', 500);
            $table->text('content');
            $table->integer('chunk_index')->default(0);
            $table->string('title', 255)->nullable();
            $table->jsonb('metadata')->nullable();
            $table->vector('embedding', {dimensions})->nullable();
            $table->timestamps();

            $table->index('file_path');
        });

        // Create HNSW index for fast similarity search
        DB::statement('CREATE INDEX {table}_embedding_idx ON {table} USING hnsw (embedding vector_cosine_ops)');
    }

    public function down(): void
    {
        Schema::dropIfExists('{table}');
    }
};
```

**Replace placeholders:**
- `{table}` → table name (default: `doc_embeddings`)
- `{dimensions}` → vector dimensions (default: `1536`)

---

### TEMPLATE: PRISMA

**Append to:** `prisma/schema.prisma`

First, ensure the `postgresqlExtensions` preview feature is enabled in the generator block.

```prisma
model DocEmbedding {
  id          String   @id @default(uuid())
  filePath    String   @map("file_path") @db.VarChar(500)
  content     String   @db.Text
  chunkIndex  Int      @default(0) @map("chunk_index")
  title       String?  @db.VarChar(255)
  metadata    Json?
  embedding   Unsupported("vector({dimensions})")?
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  @@index([filePath])
  @@map("{table}")
}
```

**Additional instructions for Prisma:**

```
📝 Prisma Setup Instructions

1. Add the vector extension to your schema.prisma:

   generator client {
     provider        = "prisma-client-js"
     previewFeatures = ["postgresqlExtensions"]
   }

   datasource db {
     provider   = "postgresql"
     url        = env("DATABASE_URL")
     extensions = [vector]
   }

2. Run migration:
   npx prisma migrate dev --name add_doc_embeddings

3. For vector operations, use raw SQL or pgvector-compatible library
```

---

### TEMPLATE: TYPEORM

**Create file:** `src/migrations/{timestamp}-CreateDocEmbeddings.ts`

```typescript
import { MigrationInterface, QueryRunner, Table, TableIndex } from "typeorm";

export class CreateDocEmbeddings{timestamp} implements MigrationInterface {
    public async up(queryRunner: QueryRunner): Promise<void> {
        // Enable pgvector extension
        await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS vector`);

        await queryRunner.createTable(
            new Table({
                name: "{table}",
                columns: [
                    {
                        name: "id",
                        type: "uuid",
                        isPrimary: true,
                        generationStrategy: "uuid",
                        default: "gen_random_uuid()",
                    },
                    {
                        name: "file_path",
                        type: "varchar",
                        length: "500",
                    },
                    {
                        name: "content",
                        type: "text",
                    },
                    {
                        name: "chunk_index",
                        type: "integer",
                        default: 0,
                    },
                    {
                        name: "title",
                        type: "varchar",
                        length: "255",
                        isNullable: true,
                    },
                    {
                        name: "metadata",
                        type: "jsonb",
                        isNullable: true,
                    },
                    {
                        name: "created_at",
                        type: "timestamp with time zone",
                        default: "CURRENT_TIMESTAMP",
                    },
                    {
                        name: "updated_at",
                        type: "timestamp with time zone",
                        default: "CURRENT_TIMESTAMP",
                    },
                ],
            }),
            true
        );

        // Add vector column
        await queryRunner.query(
            `ALTER TABLE {table} ADD COLUMN embedding vector({dimensions})`
        );

        // Create indexes
        await queryRunner.createIndex(
            "{table}",
            new TableIndex({
                name: "idx_{table}_file_path",
                columnNames: ["file_path"],
            })
        );

        await queryRunner.query(
            `CREATE INDEX idx_{table}_embedding ON {table} USING hnsw (embedding vector_cosine_ops)`
        );
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.dropTable("{table}");
    }
}
```

---

### TEMPLATE: DRIZZLE

**Create file:** `src/db/schema/docEmbeddings.ts`

```typescript
import { pgTable, uuid, varchar, text, integer, jsonb, timestamp, index } from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

// Note: Drizzle doesn't have native vector support, use customType
import { customType } from "drizzle-orm/pg-core";

const vector = customType<{ data: number[]; driverData: string }>({
    dataType() {
        return `vector({dimensions})`;
    },
    toDriver(value: number[]): string {
        return JSON.stringify(value);
    },
    fromDriver(value: string): number[] {
        return JSON.parse(value);
    },
});

export const {table} = pgTable(
    "{table}",
    {
        id: uuid("id").primaryKey().defaultRandom(),
        filePath: varchar("file_path", { length: 500 }).notNull(),
        content: text("content").notNull(),
        chunkIndex: integer("chunk_index").default(0),
        title: varchar("title", { length: 255 }),
        metadata: jsonb("metadata"),
        embedding: vector("embedding"),
        createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
        updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
    },
    (table) => ({
        filePathIdx: index("idx_{table}_file_path").on(table.filePath),
    })
);
```

**Create migration file:** `drizzle/{timestamp}_add_doc_embeddings.sql`

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS {table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    title VARCHAR(255),
    metadata JSONB,
    embedding vector({dimensions}),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_{table}_file_path ON {table}(file_path);
CREATE INDEX IF NOT EXISTS idx_{table}_embedding ON {table} USING hnsw (embedding vector_cosine_ops);
```

---

### TEMPLATE: DJANGO

**Create file:** `{app}/migrations/{NNNN}_create_doc_embeddings.py`

```python
from django.db import migrations, models
from pgvector.django import VectorField, HnswIndex
import uuid


class Migration(migrations.Migration):

    dependencies = [
        # Add your app's last migration here
    ]

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector;"),
        migrations.CreateModel(
            name="DocEmbedding",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("file_path", models.CharField(max_length=500, db_index=True)),
                ("content", models.TextField()),
                ("chunk_index", models.IntegerField(default=0)),
                ("title", models.CharField(max_length=255, null=True, blank=True)),
                ("metadata", models.JSONField(null=True, blank=True)),
                ("embedding", VectorField(dimensions={dimensions}, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "{table}",
                "indexes": [
                    HnswIndex(
                        name="{table}_embedding_idx",
                        fields=["embedding"],
                        m=16,
                        ef_construction=64,
                        opclasses=["vector_cosine_ops"],
                    ),
                ],
            },
        ),
    ]
```

**Additional instructions for Django:**

```
📝 Django Setup Instructions

1. Install pgvector-python:
   pip install pgvector

2. Add to your model (optional, for ORM access):

   from pgvector.django import VectorField

   class DocEmbedding(models.Model):
       id = models.UUIDField(primary_key=True, default=uuid.uuid4)
       file_path = models.CharField(max_length=500, db_index=True)
       content = models.TextField()
       chunk_index = models.IntegerField(default=0)
       title = models.CharField(max_length=255, null=True)
       metadata = models.JSONField(null=True)
       embedding = VectorField(dimensions={dimensions}, null=True)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)

       class Meta:
           db_table = "{table}"

3. Run migration:
   python manage.py migrate
```

---

### TEMPLATE: RAW SQL (FALLBACK)

**Create file:** `migrations/create_doc_embeddings.sql` or `sql/create_doc_embeddings.sql`

```sql
-- =============================================================================
-- Migration: Create doc_embeddings table for documentation vector storage
-- Database: PostgreSQL with pgvector extension
-- Embedding Model: text-embedding-3-small ({dimensions} dimensions)
-- =============================================================================

-- Enable pgvector extension (requires superuser or extension already installed)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create doc_embeddings table
CREATE TABLE IF NOT EXISTS {table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    title VARCHAR(255),
    metadata JSONB,
    embedding vector({dimensions}),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on file_path for fast lookups
CREATE INDEX IF NOT EXISTS idx_{table}_file_path ON {table}(file_path);

-- HNSW index for fast similarity search (cosine distance)
-- HNSW is faster for queries but slower to build than IVFFlat
CREATE INDEX IF NOT EXISTS idx_{table}_embedding ON {table} USING hnsw (embedding vector_cosine_ops);

-- Update trigger for updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
CREATE TRIGGER update_{table}_updated_at
    BEFORE UPDATE ON {table}
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Rollback (run manually if needed):
-- DROP TABLE IF EXISTS {table};
-- =============================================================================
```

---

## STEP 4: POST-GENERATION INSTRUCTIONS

After generating the migration file, display:

```
✅ Migration Generated Successfully!

📄 Created: {path_to_migration_file}

📋 Table Structure:
   ┌────────────────┬─────────────────────┬──────────────────────────────┐
   │ Column         │ Type                │ Description                  │
   ├────────────────┼─────────────────────┼──────────────────────────────┤
   │ id             │ UUID                │ Primary key                  │
   │ file_path      │ VARCHAR(500)        │ Path to .md file             │
   │ content        │ TEXT                │ Document content             │
   │ chunk_index    │ INTEGER             │ Chunk number (for large docs)│
   │ title          │ VARCHAR(255)        │ Document title               │
   │ metadata       │ JSONB               │ Flexible metadata            │
   │ embedding      │ VECTOR({dimensions})│ OpenAI embedding             │
   │ created_at     │ TIMESTAMP           │ Creation timestamp           │
   │ updated_at     │ TIMESTAMP           │ Last update timestamp        │
   └────────────────┴─────────────────────┴──────────────────────────────┘

📊 Indexes:
   • file_path - B-tree index for path lookups
   • embedding - HNSW index for vector similarity search

🚀 Next Steps:

{FOR LARAVEL}
1. Run the migration:
   php artisan migrate

2. Verify the table was created:
   php artisan tinker
   >>> \DB::select("SELECT * FROM {table} LIMIT 1");

{FOR PRISMA}
1. Run the migration:
   npx prisma migrate dev --name add_doc_embeddings

2. Generate the client:
   npx prisma generate

{FOR TYPEORM}
1. Run the migration:
   npx typeorm migration:run

{FOR DRIZZLE}
1. Run the migration:
   npx drizzle-kit push:pg

{FOR DJANGO}
1. Run the migration:
   python manage.py migrate

{FOR RAW SQL}
1. Connect to your PostgreSQL database and run the SQL file:
   psql -d your_database -f migrations/create_doc_embeddings.sql

{FOR ALL}
💡 Coming Soon: /docs:import
   Import your documentation into the vector database for semantic search.

📚 Embedding Model: text-embedding-3-small
   Dimensions: {dimensions}
   Cost: ~$0.02 per 1M tokens
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| PostgreSQL not detected | Warn that pgvector requires PostgreSQL |
| pgvector not installed | Provide installation instructions |
| Migration file exists | Ask to overwrite or use different name |
| No framework detected | Use raw SQL fallback |
| Invalid dimensions | Show valid options (1536, 3072) |

---

## TIPS

- The HNSW index is optimized for read-heavy workloads (documentation search)
- For large datasets (>1M rows), consider IVFFlat index instead
- `chunk_index` allows storing large documents in multiple chunks
- `metadata` can store tags, module names, categories, etc.
- Always create the pgvector extension before the table
