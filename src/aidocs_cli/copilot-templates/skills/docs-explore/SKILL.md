---
name: docs:explore
description: |
  # Documentation Exploration Skill
  
  Interactively explore and document code in the JobMatix-API project.
  
  ## What this skill does:
  
  1. Uses interactive exploration to understand application behavior
  2. Discovers UI behavior, conditional fields, and state changes
  3. Documents user flows and interactions
  4. Generates comprehensive documentation based on exploration
tags: [documentation]
---

# Documentation Exploration Skill

Interactively explore and document code in the JobMatix-API project.

## What this skill does:

1. Uses interactive exploration to understand application behavior
2. Discovers UI behavior, conditional fields, and state changes
3. Documents user flows and interactions
4. Generates comprehensive documentation based on exploration

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/explore/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "explore the campaigns module"
- "document this feature interactively"
- "explore app/Domains/Campaigns"
- "interactively document the user flow"

## Key Features:

- Interactive UI exploration
- Conditional field discovery
- State change documentation
- User flow mapping

## Arguments:

Supports path arguments and options:
```
explore app/Domains/Campaigns
explore --depth=2
explore app/Services
```
