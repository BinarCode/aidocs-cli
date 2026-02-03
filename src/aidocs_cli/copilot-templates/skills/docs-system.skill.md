# Documentation System Skill

AI-powered documentation assistant for JobMatix-API. This skill provides intelligent documentation management.

## Available Actions:

### Getting Started
- **init** - Initialize documentation settings (run this first!)
- **discover** - Discover and map codebase structure

### Interactive Documentation
- **explore** - Interactively explore and document code
- **analyze** - Analyze existing documentation coverage
- **generate** - Generate documentation for specific files/sections
- **update** - Update existing documentation

### Advanced Features
- **plan** - Create a documentation plan for the project
- **execute** - Execute a documentation plan
- **flow** - Document process flows and architecture
- **batch** - Batch process multiple files
- **export-pdf** - Export documentation to PDF

### RAG (Retrieval-Augmented Generation)
- **rag-init** - Initialize RAG vector database
- **rag** - Query documentation using RAG
- **rag-vectors** - Manage documentation vectors

## How It Works:

When the user requests any documentation action, locate and load the corresponding workflow file from:
`.copilot/workflows/docs/{action}/workflow.md`

Then follow the instructions in that workflow file exactly.

## Workflow File Locations:

- init: `.copilot/workflows/docs/init/workflow.md`
- discover: `.copilot/workflows/docs/discover/workflow.md`
- explore: `.copilot/workflows/docs/explore/workflow.md`
- analyze: `.copilot/workflows/docs/analyze/workflow.md`
- generate: `.copilot/workflows/docs/generate/workflow.md`
- update: `.copilot/workflows/docs/update/workflow.md`
- plan: `.copilot/workflows/docs/plan/workflow.md`
- execute: `.copilot/workflows/docs/execute/workflow.md`
- flow: `.copilot/workflows/docs/flow/workflow.md`
- batch: `.copilot/workflows/docs/batch/workflow.md`
- export-pdf: `.copilot/workflows/docs/export-pdf/workflow.md`
- rag-init: `.copilot/workflows/docs/rag-init/workflow.md`
- rag: `.copilot/workflows/docs/rag/workflow.md`
- rag-vectors: `.copilot/workflows/docs/rag-vectors/workflow.md`

## Usage Examples:

```
initialize documentation
document this code
explore the codebase and create docs
analyze documentation coverage
generate docs for app/Models/User.php
create a documentation plan
```

## Important:

Always load the workflow file from the PROJECT directory (JobMatix-API/.copilot/workflows/docs/), not from the global ~/.copilot/ directory.
