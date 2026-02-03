---
name: docs:generate
description: |
  # Documentation Generation Skill
  
  Generate documentation for specific files, components, or web pages in JobMatix-API.
  
  ## What this skill does:
  
  1. Generates documentation for specific files or sections
  2. Can analyze web pages using browser automation
  3. Uses AI vision for page analysis when needed
  4. Creates structured, consistent documentation
tags: [documentation]
---

# Documentation Generation Skill

Generate documentation for specific files, components, or web pages in JobMatix-API.

## What this skill does:

1. Generates documentation for specific files or sections
2. Can analyze web pages using browser automation
3. Uses AI vision for page analysis when needed
4. Creates structured, consistent documentation

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/generate/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "generate docs for app/Models/User.php"
- "document this service"
- "generate documentation for the campaigns page"
- "create docs for this component"

## Arguments:

For files:
```
generate app/Services/PaymentService.php
generate app/Domains/Campaigns/Actions/CreateCampaignAction.php
```

For web pages:
```
generate <url>
generate --auth user:pass
generate --output ./docs
```

## Output:

- Markdown documentation
- Code examples
- API documentation
- Usage instructions
