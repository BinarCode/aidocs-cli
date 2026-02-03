---
name: docs:execute
description: |
  # Documentation Execution Skill
  
  Execute the documentation plan and generate all planned documentation.
  
  ## What this skill does:
  
  1. Loads the documentation plan
  2. Executes documentation generation for all planned items
  3. Tracks progress through the plan
  4. Generates comprehensive documentation for the entire project
tags: [documentation]
---

# Documentation Execution Skill

Execute the documentation plan and generate all planned documentation.

## What this skill does:

1. Loads the documentation plan
2. Executes documentation generation for all planned items
3. Tracks progress through the plan
4. Generates comprehensive documentation for the entire project

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/execute/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Prerequisites:

Requires an existing documentation plan created by `/docs:plan`.

## Usage Patterns:

The user might say:
- "execute the documentation plan"
- "generate all planned docs"
- "implement the documentation plan"
- "start documenting everything"

## Process:

1. Reads the documentation plan
2. Processes each item in order
3. Generates documentation based on plan specifications
4. Updates progress tracking
5. Reports completion status

## Output:

- Complete documentation set based on plan
- Progress reports during execution
- Summary of completed documentation
