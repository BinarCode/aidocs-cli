---
name: docs:plan
description: |
  # Documentation Planning Skill
  
  Create comprehensive documentation plans for the JobMatix-API project.
  
  ## What this skill does:
  
  1. Creates a structured documentation plan based on discovered modules
  2. Prioritizes documentation needs
  3. Organizes documentation tasks
  4. Provides roadmap for documentation completion
tags: [documentation]
---

# Documentation Planning Skill

Create comprehensive documentation plans for the JobMatix-API project.

## What this skill does:

1. Creates a structured documentation plan based on discovered modules
2. Prioritizes documentation needs
3. Organizes documentation tasks
4. Provides roadmap for documentation completion

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/plan/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Prerequisites:

Should be run after `/docs:discover` has completed and created the knowledge base.

## Usage Patterns:

The user might say:
- "create a documentation plan"
- "plan out the documentation work"
- "what docs do we need?"
- "create a docs roadmap"

## Output:

Creates a documentation plan file with:
- Prioritized list of modules to document
- Documentation types needed for each module
- Estimated scope and complexity
- Suggested order of completion

## Next Steps:

After creating a plan, suggest running:
- `/docs:execute` to execute the plan
- `/docs:generate` for specific high-priority items
