---
name: docs:flow
description: |
  # Documentation Flow Skill
  
  Document features with screenshots and step-by-step instructions.
  
  ## What this skill does:
  
  1. Documents complete feature flows
  2. Captures screenshots at each step
  3. Creates step-by-step instructions
  4. Can generate technical or user-focused documentation
tags: [documentation]
---

# Documentation Flow Skill

Document features with screenshots and step-by-step instructions.

## What this skill does:

1. Documents complete feature flows
2. Captures screenshots at each step
3. Creates step-by-step instructions
4. Can generate technical or user-focused documentation

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/flow/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "document the order processing flow"
- "create flow documentation for campaigns"
- "document this feature with screenshots"
- "flow document the checkout process"

## Arguments:

```
flow "Order Processing"
flow "Campaign Creation" --technical
flow "User Registration"
```

## Options:

- `--technical` - Generate developer-focused output
- Default is user-focused documentation

## Output:

- Step-by-step documentation
- Screenshots for each step
- State transitions
- Decision points
- Error scenarios
