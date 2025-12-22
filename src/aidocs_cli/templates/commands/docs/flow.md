---
name: docs:flow
description: Document a code flow by analyzing the codebase from a human description. No browser required.
---

# Document a Code Flow

Analyze your codebase to document how a specific feature or process works based on a natural language description.

**Usage:**
```
/docs:flow "<description>"
/docs:flow "sync users from discord"
/docs:flow "how payments are processed"
/docs:flow "user registration and onboarding"
/docs:flow "webhook handling for stripe events"
```

**Arguments:**
- `"description"` - Natural language description of the flow to document (in quotes)

**What it does:**
1. Parses your description to extract keywords and intent
2. Searches the codebase for relevant files (jobs, services, controllers, etc.)
3. Identifies entry points (commands, jobs, webhooks, routes)
4. Traces the execution flow and builds a call graph
5. Generates a mermaid sequence diagram
6. Extracts relevant code snippets with file:line references
7. Creates comprehensive markdown documentation

**Output:**
- `docs/flows/{kebab-case-title}.md` - Complete flow documentation

**Example output for `/docs:flow "sync users from discord"`:**
- Overview of what the flow does
- Mermaid sequence diagram showing data flow
- Entry points (scheduled job, artisan command, webhook)
- Step-by-step code walkthrough with snippets
- Related files table
- Trigger methods (manual, scheduled, event-driven)

**No dependencies required** - Uses only codebase analysis (grep, read).

---

**Execute workflow:** `@.claude/workflows/docs/flow/workflow.md`
