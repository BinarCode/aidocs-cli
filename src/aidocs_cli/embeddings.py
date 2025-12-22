"""Embedding generation and SQL export for vector DB import."""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

OPENAI_API_URL = "https://api.openai.com/v1/embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_RETRIES = 3
RETRY_DELAY = 1.0


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    return os.environ.get("OPENAI_API_KEY")


def generate_embedding(text: str, api_key: str) -> Optional[list[float]]:
    """Generate embedding for a single text using OpenAI API.

    Args:
        text: Text to embed
        api_key: OpenAI API key

    Returns:
        List of floats (embedding vector) or None on error
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
    }

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    OPENAI_API_URL,
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["data"][0]["embedding"]
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    return None

        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None

    return None


def generate_embeddings_batch(
    texts: list[str],
    api_key: str,
    on_progress: Optional[callable] = None,
) -> list[Optional[list[float]]]:
    """Generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed
        api_key: OpenAI API key
        on_progress: Optional callback(index, total, text_preview)

    Returns:
        List of embeddings (or None for failed items)
    """
    embeddings = []

    for i, text in enumerate(texts):
        if on_progress:
            preview = text[:50] + "..." if len(text) > 50 else text
            on_progress(i, len(texts), preview)

        embedding = generate_embedding(text, api_key)
        embeddings.append(embedding)

        # Small delay to avoid rate limits
        if i < len(texts) - 1:
            time.sleep(0.1)

    return embeddings


def format_embedding_for_sql(embedding: list[float]) -> str:
    """Format embedding vector for PostgreSQL pgvector."""
    # Format as '[0.001, 0.002, ...]'::vector
    values = ", ".join(f"{v:.8f}" for v in embedding)
    return f"'[{values}]'::vector"


def escape_sql_string(s: str) -> str:
    """Escape a string for SQL insertion."""
    # Escape single quotes by doubling them
    return s.replace("'", "''")


def load_manifest(docs_dir: Path) -> Optional[dict]:
    """Load the chunks manifest file."""
    manifest_path = docs_dir / ".chunks" / "manifest.json"

    if not manifest_path.exists():
        return None

    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_chunks_file(chunks_path: Path) -> Optional[dict]:
    """Load a chunks JSON file."""
    if not chunks_path.exists():
        return None

    try:
        return json.loads(chunks_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_last_sync(docs_dir: Path) -> dict:
    """Load the last sync state."""
    sync_path = docs_dir / ".chunks" / "last-sync.json"

    if sync_path.exists():
        try:
            return json.loads(sync_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "synced_at": None,
        "files": {},
    }


def save_last_sync(docs_dir: Path, sync_state: dict) -> None:
    """Save the last sync state."""
    chunks_dir = docs_dir / ".chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    sync_path = chunks_dir / "last-sync.json"
    sync_path.write_text(
        json.dumps(sync_state, indent=2),
        encoding="utf-8",
    )


def generate_sync_sql(
    docs_dir: Path,
    force: bool = False,
    dry: bool = False,
    table_name: str = "doc_embeddings",
    on_progress: Optional[callable] = None,
    on_status: Optional[callable] = None,
) -> dict:
    """Generate SQL for syncing documentation to vector DB.

    Args:
        docs_dir: Documentation directory
        force: Re-sync all files regardless of previous sync
        dry: Preview only, don't generate embeddings
        table_name: Name of the target table
        on_progress: Progress callback(current, total, message)
        on_status: Status callback(message)

    Returns:
        Dict with stats and results
    """
    api_key = get_openai_api_key()
    if not api_key and not dry:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not set",
            "stats": {},
        }

    manifest = load_manifest(docs_dir)
    if not manifest:
        return {
            "success": False,
            "error": "No manifest found. Run 'aidocs rag-chunks' first.",
            "stats": {},
        }

    last_sync = load_last_sync(docs_dir)

    # Analyze what needs to be synced
    to_sync = []
    to_delete = []
    unchanged = []

    # Check for files to sync or update
    for rel_path, file_info in manifest["files"].items():
        file_hash = file_info.get("hash")
        chunks_file = file_info.get("chunks_file")

        if not chunks_file:
            continue

        chunks_path = Path(chunks_file)
        if not chunks_path.exists():
            continue

        # Check if file changed since last sync
        last_synced = last_sync["files"].get(rel_path, {})

        if not force and last_synced.get("hash") == file_hash:
            unchanged.append(rel_path)
            continue

        chunks_data = load_chunks_file(chunks_path)
        if chunks_data:
            to_sync.append({
                "path": rel_path,
                "hash": file_hash,
                "chunks_data": chunks_data,
                "is_update": rel_path in last_sync["files"],
            })

    # Check for deleted files
    for rel_path in last_sync["files"]:
        if rel_path not in manifest["files"]:
            to_delete.append(rel_path)

    # Calculate stats
    total_chunks = sum(len(item["chunks_data"]["chunks"]) for item in to_sync)

    stats = {
        "unchanged": len(unchanged),
        "to_sync": len(to_sync),
        "to_delete": len(to_delete),
        "total_chunks": total_chunks,
        "estimated_tokens": total_chunks * 500,  # rough estimate
        "estimated_cost": total_chunks * 500 * 0.00002 / 1000,  # $0.02/1M tokens
    }

    if dry:
        return {
            "success": True,
            "dry": True,
            "stats": stats,
            "to_sync": [item["path"] for item in to_sync],
            "to_delete": to_delete,
            "unchanged": unchanged,
        }

    if not to_sync and not to_delete:
        return {
            "success": True,
            "stats": stats,
            "message": "Nothing to sync - all files up to date",
        }

    # Generate embeddings and SQL
    if on_status:
        on_status("Generating embeddings...")

    sql_statements = []
    sql_statements.append(f"-- Documentation Sync SQL")
    sql_statements.append(f"-- Generated by aidocs rag-vectors at {datetime.now(timezone.utc).isoformat()}")
    sql_statements.append(f"-- Run with: psql $DATABASE_URL -f docs/.chunks/sync.sql")
    sql_statements.append("")
    sql_statements.append("BEGIN;")
    sql_statements.append("")

    # Delete statements for removed files
    for rel_path in to_delete:
        sql_statements.append(f"-- Delete removed file: {rel_path}")
        sql_statements.append(f"DELETE FROM {table_name} WHERE file_path = '{escape_sql_string(rel_path)}';")
        sql_statements.append("")

    # Process files to sync
    new_sync_state = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "files": {},
    }

    # Keep unchanged files in sync state
    for rel_path in unchanged:
        if rel_path in last_sync["files"]:
            new_sync_state["files"][rel_path] = last_sync["files"][rel_path]

    embeddings_generated = 0
    tokens_used = 0

    for item in to_sync:
        rel_path = item["path"]
        file_hash = item["hash"]
        chunks_data = item["chunks_data"]
        is_update = item["is_update"]

        if is_update:
            sql_statements.append(f"-- Update file: {rel_path}")
            sql_statements.append(f"DELETE FROM {table_name} WHERE file_path = '{escape_sql_string(rel_path)}';")
        else:
            sql_statements.append(f"-- New file: {rel_path}")

        for chunk in chunks_data["chunks"]:
            chunk_index = chunk["chunk_index"]
            title = chunk.get("title", "")
            content = chunk["content"]
            hierarchy = chunk.get("hierarchy", [])
            metadata = chunk.get("metadata", {})

            # Add hierarchy to metadata
            metadata["hierarchy"] = hierarchy

            # Generate embedding
            if on_progress:
                on_progress(
                    embeddings_generated,
                    total_chunks,
                    f"{rel_path}#{title[:30]}"
                )

            embedding = generate_embedding(content, api_key)

            if embedding:
                embeddings_generated += 1
                tokens_used += len(content.split()) * 1.3  # rough token estimate

                embedding_sql = format_embedding_for_sql(embedding)
                metadata_sql = escape_sql_string(json.dumps(metadata))

                sql_statements.append(f"""INSERT INTO {table_name} (file_path, content, chunk_index, title, metadata, embedding)
VALUES (
  '{escape_sql_string(rel_path)}',
  '{escape_sql_string(content)}',
  {chunk_index},
  '{escape_sql_string(title)}',
  '{metadata_sql}'::jsonb,
  {embedding_sql}
);""")
            else:
                sql_statements.append(f"-- ERROR: Failed to generate embedding for chunk {chunk_index}")

        sql_statements.append("")

        # Update sync state
        new_sync_state["files"][rel_path] = {
            "hash": file_hash,
            "chunk_count": len(chunks_data["chunks"]),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

    sql_statements.append("COMMIT;")
    sql_statements.append("")
    sql_statements.append(f"-- Summary:")
    sql_statements.append(f"-- Deleted: {len(to_delete)} file(s)")
    sql_statements.append(f"-- Synced: {len(to_sync)} file(s)")
    sql_statements.append(f"-- Embeddings: {embeddings_generated}")

    # Write SQL file
    sql_content = "\n".join(sql_statements)
    sql_path = docs_dir / ".chunks" / "sync.sql"
    sql_path.write_text(sql_content, encoding="utf-8")

    # Save sync state
    save_last_sync(docs_dir, new_sync_state)

    stats["embeddings_generated"] = embeddings_generated
    stats["tokens_used"] = int(tokens_used)
    stats["sql_file"] = str(sql_path)

    return {
        "success": True,
        "stats": stats,
        "sql_file": str(sql_path),
    }
