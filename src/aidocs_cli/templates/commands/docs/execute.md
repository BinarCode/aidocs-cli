---
name: docs:execute
description: Execute the documentation plan and generate all docs
---

# Execute Documentation Plan

Run through `docs-plan.yaml` and generate documentation for each module.

**Usage:**
```
/docs:execute                      # Execute full plan
/docs:execute --module campaigns   # Execute only one module
/docs:execute --continue           # Continue from where it stopped
/docs:execute --dry                # Preview what would be generated
```

**What it does:**
1. Reads `docs-plan.yaml`
2. For each module in order:
   - Runs explore (if needed)
   - Generates lifecycle documentation
   - Captures screenshots
   - Writes to `docs/{module}/`
3. Updates plan status as it progresses
4. Generates cross-module flows last

**Progress tracking:**
```
📋 Executing Documentation Plan

[1/4] users
  ✓ Exploring UI...
  ✓ Documenting lifecycle...
  ✓ Screenshots captured: 8
  ✓ Written: docs/users/

[2/4] campaigns
  → Exploring UI...

Status: 1 complete, 1 in progress, 2 pending
```

**Output structure:**
```
docs/
├── index.md                    # Auto-updated with links
├── users/
│   ├── index.md               # Module overview
│   ├── lifecycle.md           # CRUD documentation
│   ├── registration-to-campaign.md  # Cross-module flow (first module)
│   └── images/
└── campaigns/
    ├── index.md
    ├── lifecycle.md
    ├── duplicate-campaign.md  # Custom flow
    └── images/
```

**Resume support:**
If execution stops (error, timeout, manual stop):
- Plan status is saved
- Run `/docs:execute --continue` to resume

---

**Execute workflow:** `@.claude/workflows/docs/execute/workflow.md`
