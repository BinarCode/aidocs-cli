---
name: docs:explore
description: Interactive exploration of the application using Playwright to discover UI behavior, conditional fields, and state changes
---

# Explore Application Interactively

Use Playwright to systematically explore your application, discovering UI behaviors, conditional fields, form validation, and state changes.

**Usage:**
```
/docs:explore [url] [--depth deep|medium|shallow] [--record]
```

**Arguments:**
- `url` (optional) - Starting URL, or explores from base URL in config
- `--depth` - How thoroughly to explore (default: medium)
- `--record` - Record a video of the exploration

**What it does:**
1. Navigates to each page systematically
2. Identifies all interactive elements (buttons, links, inputs, checkboxes)
3. Clicks each element and observes what changes
4. Fills forms with test data to discover validation
5. Tracks state changes across pages
6. Maps conditional UI (what appears when you click a checkbox)
7. Records API calls made during interactions

**Output:** Updates `docs/.knowledge/` with:
- `ui-states.json` - UI state machine for each page
- `interactions.json` - What happens when you click/fill each element
- `validation-messages.json` - Actual validation messages from the UI
- `api-calls.json` - API endpoints called during interactions

---

**Execute workflow:** `@docs-workflows/explore/workflow.md`
