---
name: docs:update
description: Update documentation based on code changes in current branch
---

# Update Documentation from Code Changes

Update existing documentation based on git diff between your current branch and a base branch.

**Usage:**
```
/docs:update [--base main] [--output ./docs]
```

**Arguments:**
- `--base` - Base branch to diff against (default: main)
- `--output` - Documentation directory (default from config or ./docs)

**What it does:**
1. Gets git diff between current branch and base branch
2. Identifies changed routes, components, and features
3. Finds related existing documentation
4. Updates docs to reflect the code changes
5. Optionally captures new screenshots if UI changed

---

**Execute workflow:** `@.claude/workflows/docs/update/workflow.md`
