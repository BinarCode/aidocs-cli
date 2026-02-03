---
name: docs:analyze
description: |
  # Documentation Analysis Skill
  
  Analyze codebase for documentation coverage and specific routes/components.
  
  ## What this skill does:
  
  1. Analyzes existing documentation coverage
  2. Identifies undocumented code areas
  3. Performs pure code analysis without requiring browser
  4. Analyzes specific routes or components on request
tags: [documentation]
---

# Documentation Analysis Skill

Analyze codebase for documentation coverage and specific routes/components.

## What this skill does:

1. Analyzes existing documentation coverage
2. Identifies undocumented code areas
3. Performs pure code analysis without requiring browser
4. Analyzes specific routes or components on request

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/analyze/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "analyze documentation coverage"
- "check what's documented"
- "analyze the campaigns route"
- "analyze this component"

## Arguments:

```
analyze <route>
analyze --codebase ./src
analyze app/Http/Controllers/CampaignController.php
```

## Output:

- Coverage statistics
- List of undocumented areas
- Suggestions for improvement
- Priority recommendations
