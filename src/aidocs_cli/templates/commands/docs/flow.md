---
name: docs:flow
description: Document a complete entity lifecycle or user flow with cross-page tracking
---

# Document a Complete Flow

Generate comprehensive documentation for an entity lifecycle (create → view → edit → delete) or a custom user flow that spans multiple pages.

**Usage:**
```
/docs:flow <entity|"custom flow description">
/docs:flow campaign
/docs:flow "user registration to first purchase"
/docs:flow order --lifecycle
```

**Arguments:**
- `entity` - Entity name to document its full CRUD lifecycle
- `"description"` - Custom flow description in quotes
- `--lifecycle` - Document full create/read/update/delete cycle
- `--include-errors` - Also document error states and edge cases

**What it does:**
1. Uses knowledge base to understand entity/flow
2. Navigates through the complete flow with Playwright
3. Captures screenshots at each step
4. Documents data that appears across pages
5. Shows where created data appears in lists/dashboards
6. Documents validation at each step
7. Captures success/error states

**Example output for `/docs:flow campaign --lifecycle`:**
- How to create a campaign (with validation)
- Where the campaign appears after creation
- How to view campaign details
- How to edit a campaign
- How to delete a campaign
- Related: What happens to campaign data elsewhere

---

**Execute workflow:** `@docs-workflows/flow/workflow.md`
