---
name: docs-update
description: Update existing documentation based on git diff between current branch and base branch.
---

# Documentation Update Workflow

**Goal:** Analyze code changes in the current branch and update relevant documentation to reflect those changes.

**Your Role:** You are a documentation maintainer. You will analyze the git diff, identify what changed, find related docs, and update them to stay in sync with the code.

---

## STEP 0: FIND AND LOAD CONFIGURATION

**CRITICAL:** Before doing anything else, locate and load the configuration file.

### 0.1 Search for Config File

Search for `aidocs-config.yml` in this order:
1. `docs/aidocs-config.yml` (default location)
2. `./aidocs-config.yml` (project root)

**Also check for old config format:**
If `docs/config.yml` exists but `aidocs-config.yml` doesn't:
```
⚠️  Found old config format: docs/config.yml

Please rename it to: docs/aidocs-config.yml
Then run this command again.
```

### 0.2 If Config Found

Load the config and extract:
- `docs_root` → Base directory for all documentation (default: `docs`)
- `style.tone` → Writing style to maintain
- `stack` → Tech stack info for understanding changes

### 0.3 If Config NOT Found

Display message and STOP:
```
⚠️  No aidocs-config.yml found.

This workflow requires a configuration file to run.

Would you like to create one now?
1. Yes - run /docs:init to set up configuration
2. No - I'll create docs/aidocs-config.yml manually
```

**IMPORTANT:** Do NOT proceed without config. Config is required.

---

## ARGUMENTS PARSING

Parse the arguments passed to this workflow:
```
/docs:update [--base main|staging|<branch>] [--output ./{docs_root}] [--dry-run] [--screenshots]
```

Extract:
- `base` (optional) - Branch to diff against (default: main)
- `output` (optional) - Docs directory (default from config `docs_root`)
- `dry-run` (optional) - Show what would be updated without making changes
- `screenshots` (optional) - Capture new screenshots for changed pages

If not provided, ask:
```
Which branch should I compare against?

1. main (default)
2. staging
3. develop
4. Other (specify)
```

---

## STEP 1: GET GIT DIFF

Run git commands to understand what changed:

```bash
# Get current branch name
git branch --show-current

# Get list of changed files
git diff <base_branch>...HEAD --name-only

# Get detailed diff for analysis
git diff <base_branch>...HEAD --stat

# Get full diff content for changed files
git diff <base_branch>...HEAD
```

**Store the results:**
- Current branch name
- List of all changed files
- Summary statistics
- Full diff content

---

## STEP 2: ANALYZE CHANGES

Categorize the changed files:

### 2.1 Frontend Changes
Look for changes in:
- `*.vue`, `*.tsx`, `*.jsx` → Component changes
- `pages/`, `views/`, `screens/` → Page/route changes
- `components/` → Reusable component changes
- `*.css`, `*.scss`, `styles/` → Style changes (may affect screenshots)

For each changed frontend file, extract:
- Component/page name
- What functionality changed (from diff)
- New props, events, or methods
- UI changes (new buttons, forms, fields)

### 2.2 Backend Changes
Look for changes in:
- `routes/`, `api/` → Route changes
- `controllers/`, `handlers/` → Business logic changes
- `models/`, `entities/` → Data model changes
- `validators/`, `requests/` → Validation rule changes

For each changed backend file, extract:
- Affected endpoints/routes
- New or modified validation rules
- Changed response formats
- New side effects (emails, notifications)

### 2.3 Determine Affected Pages/Features
Map code changes to user-facing features:

```
Changed Files → Affected Features
─────────────────────────────────
components/CampaignForm.vue → Campaign creation/editing
pages/campaigns/index.vue → Campaigns list page
api/campaigns.php → Campaign CRUD operations
```

Output summary:
```
📊 Change Analysis

Branch: feature/add-campaign-tags
Comparing against: main
Files changed: 8

Frontend changes:
  • components/CampaignForm.vue - Added tags field
  • pages/campaigns/[id].vue - Display tags in detail view

Backend changes:
  • app/Http/Controllers/CampaignController.php - Tags CRUD
  • app/Models/Campaign.php - Tags relationship

Affected features:
  • Campaign creation (new tags field)
  • Campaign detail page (tags display)
  • Campaign editing (tags management)
```

---

## STEP 3: FIND RELATED DOCUMENTATION

Search the docs directory for related files:

### 3.1 Scan Existing Docs
```bash
# List all docs
ls -la {output_directory}/*.md

# Search for mentions of affected features
grep -l "campaign" {output_directory}/*.md
```

### 3.2 Match Changes to Docs
For each affected feature, find related doc files:

| Feature | Related Doc Files |
|---------|-------------------|
| Campaign creation | `campaigns.md`, `create-campaign.md` |
| Campaign detail | `campaigns.md`, `campaign-details.md` |

### 3.3 Report Findings
```
📄 Related Documentation Found

Existing docs that may need updates:
  ✓ docs/campaigns.md - mentions campaign form
  ✓ docs/campaign-details.md - shows detail page
  ✗ docs/campaign-tags.md - NOT FOUND (may need creation)

Missing documentation:
  • No docs found for: tags feature
```

---

## STEP 4: DETERMINE UPDATE STRATEGY

For each affected doc, decide what to do:

### 4.1 Present Options
```
📝 Update Plan

1. docs/campaigns.md
   Changes needed:
   - Add "Tags" field to form documentation
   - Update Features list to include tagging
   Action: UPDATE

2. docs/campaign-details.md
   Changes needed:
   - Add Tags section showing tag display
   Action: UPDATE

3. Campaign Tags (new feature)
   No existing documentation
   Action: CREATE NEW or ADD SECTION

How would you like to proceed?

1. Apply all updates automatically
2. Review each update before applying
3. Show me what would change (dry run)
4. Skip - I'll update manually
```

---

## STEP 5: UPDATE DOCUMENTATION

### 5.1 For Each Doc to Update

**Read the existing doc:**
```
Reading: docs/campaigns.md
```

**Identify sections to modify:**
- Features list → Add new feature
- Form fields → Add new field documentation
- How-to guides → Update steps if flow changed

**Generate updated content:**
- Preserve existing structure and style
- Match the tone from config
- Add new information from code analysis
- Remove outdated information if applicable

**Apply the update:**
```markdown
## Features

- Create and manage campaigns
- Set campaign budgets and dates
- **[NEW] Add tags to organize campaigns**  ← Added
- Track campaign performance
```

### 5.2 For New Documentation Needed

If a significant new feature needs its own doc:

```
New feature detected: Campaign Tags

Would you like me to:
1. Add a section to existing campaigns.md
2. Create a new campaign-tags.md file
3. Skip for now
```

If creating new doc, use the standard template from `templates/page-doc.template.md`.

---

## STEP 6: SCREENSHOT UPDATES (if --screenshots or UI changed)

**Check if Playwright MCP is available.**

If screenshots requested and UI changed:

```
🖼️  Screenshot Updates

These pages have UI changes:
  • /campaigns - Form now includes tags field
  • /campaigns/123 - Detail page shows tags

Would you like me to capture new screenshots?

1. Yes - update all affected screenshots
2. Select specific pages
3. No - keep existing screenshots
```

If yes:
1. Navigate to each affected page
2. Capture new screenshot
3. Replace old screenshot in `{output}/images/`
4. Update image references if filename changed

---

## STEP 7: GENERATE CHANGE SUMMARY

After all updates:

```
✅ Documentation Updated

📝 Files modified:
   • docs/campaigns.md
     - Added Tags field to Features section
     - Updated form fields documentation

   • docs/campaign-details.md
     - Added Tags display section

🖼️  Screenshots updated:
   • images/campaigns.png (refreshed)
   • images/campaign-details.png (refreshed)

📊 Summary:
   • 2 docs updated
   • 2 screenshots refreshed
   • 0 new docs created

💡 Suggestions:
   • Consider adding a dedicated "Working with Tags" guide
   • Update the docs index to mention tags feature
```

---

## STEP 8: COMMIT SUGGESTION (optional)

```
Would you like me to stage the documentation changes?

Files to stage:
  • docs/campaigns.md
  • docs/campaign-details.md
  • docs/images/campaigns.png
  • docs/images/campaign-details.png

1. Yes - stage changes (git add)
2. Yes - stage and commit with message
3. No - I'll handle git myself
```

If committing, suggest message:
```
docs: update campaign documentation for tags feature

- Added tags field documentation to campaigns.md
- Updated campaign-details.md with tags display
- Refreshed screenshots

Related to: feature/add-campaign-tags
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Not a git repository | "This directory is not a git repository" |
| No changes found | "No differences found between {branch} and {base}" |
| Base branch not found | "Branch '{base}' not found. Available: main, staging, develop" |
| Docs directory missing | "Docs directory not found. Run /docs:generate first or specify --output" |
| No related docs found | "No existing documentation found for changed features. Run /docs:generate to create initial docs." |

---

## DRY RUN MODE

If `--dry-run` flag provided:

1. Perform all analysis steps (1-4)
2. Show what would be updated
3. DO NOT make any changes
4. Output preview of changes:

```
🔍 Dry Run - Preview of Changes

docs/campaigns.md:
  Line 15: + - **Add tags to organize campaigns**
  Line 42: + ### Tags
  Line 43: + Add tags to your campaign for easy filtering and organization.

docs/campaign-details.md:
  Line 28: + ## Tags
  Line 29: + Tags assigned to this campaign are displayed below the title.

No files will be modified. Remove --dry-run to apply changes.
```

---

## TIPS

- Run `/docs:update` before creating a PR to ensure docs are in sync
- Use `--dry-run` first to preview changes
- Use `--screenshots` when UI changes are significant
- Commit docs updates with your feature branch
