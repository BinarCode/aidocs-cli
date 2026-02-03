---
name: docs:update
description: |
  # Documentation Update Skill
  
  Update existing documentation based on code changes.
  
  ## What this skill does:
  
  1. Detects code changes in current branch
  2. Identifies affected documentation
  3. Updates documentation to reflect code changes
  4. Maintains documentation accuracy
tags: [documentation]
---

# Documentation Update Skill

Update existing documentation based on code changes.

## What this skill does:

1. Detects code changes in current branch
2. Identifies affected documentation
3. Updates documentation to reflect code changes
4. Maintains documentation accuracy

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/update/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "update the documentation"
- "sync docs with code changes"
- "update docs for my changes"
- "refresh documentation"

## Process:

1. Analyzes git diff in current branch
2. Identifies changed files and their documentation
3. Updates relevant documentation sections
4. Preserves manual documentation additions

## Smart Updates:

- Only updates sections affected by code changes
- Preserves custom documentation
- Maintains formatting and structure
- Suggests new documentation for new features
