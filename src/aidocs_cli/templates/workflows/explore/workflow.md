---
name: docs-explore
description: Interactive Playwright exploration of a specific module to discover UI behaviors, conditional fields, and state changes.
---

# Explore Workflow

**Goal:** Use Playwright to interactively explore a specific module's UI, discovering behaviors, conditional fields, validation messages, and state changes.

**Your Role:** You are a UI explorer. You will systematically interact with the module's pages, click buttons, fill forms, and document what happens.

**Requires:** Playwright MCP

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:explore <module> [--page <path>] [--depth shallow|medium|deep] [--record]
```

- `module` - Required: Module to explore (e.g., campaigns, users)
- `--page` - Optional: Specific page to explore (e.g., /campaigns/create)
- `--depth` - How thorough: shallow (main actions), medium (all visible), deep (hidden states)
- `--record` - Record video of exploration

**If no module:**
```
Please specify a module to explore:
  /docs:explore campaigns
  /docs:explore users --page /users/create
  /docs:explore orders --depth deep
```

---

## STEP 1: LOAD MODULE KNOWLEDGE

Check if `docs/.knowledge/modules/{module}/` exists:
- If yes: Load entity.json, components.json, routes.json
- If no: Suggest running `/docs:discover {module}` first

Load config for authentication if needed.

---

## STEP 2: IDENTIFY PAGES TO EXPLORE

Based on knowledge base or route detection:

```
📋 Pages for {module} module:

  [1] /{module}           - List page
  [2] /{module}/create    - Create form
  [3] /{module}/{id}      - Detail view
  [4] /{module}/{id}/edit - Edit form

Which pages to explore?
  1. All pages (recommended)
  2. Select specific pages
  3. Only: {--page argument}
```

---

## STEP 3: EXPLORE EACH PAGE

For each page:

### 3.1 Navigate and Authenticate

```
🔍 Exploring: /{module}/create
```

1. Navigate to page
2. Handle auth if needed (from config)
3. Wait for page load
4. Capture initial screenshot

### 3.2 Identify Interactive Elements

Scan the page for:
```javascript
// Buttons
document.querySelectorAll('button, [role="button"], input[type="submit"]')

// Form inputs
document.querySelectorAll('input, select, textarea, [contenteditable]')

// Checkboxes/Toggles
document.querySelectorAll('input[type="checkbox"], [role="switch"]')

// Links that might change state
document.querySelectorAll('a[href^="#"], [data-action], [x-on\\:click]')

// Tabs
document.querySelectorAll('[role="tab"], .tab')

// Dropdowns
document.querySelectorAll('[data-dropdown], .dropdown-trigger')
```

Output:
```
📍 Found on /{module}/create:

Forms (1):
  • CampaignForm - 8 fields

Inputs:
  • name (text, required)
  • status (select: draft, active, paused)
  • budget (number)
  • start_date (date)
  • end_date (date)
  • notifications (checkbox)
  • tags (multi-select)
  • description (textarea)

Buttons:
  • "Cancel" - navigates to /{module}
  • "Save as Draft" - submits form
  • "Save & Activate" - submits with status=active

Conditional triggers detected:
  • notifications checkbox
  • status select
```

### 3.3 Test Conditional UI

For each checkbox/toggle/select that might trigger UI changes:

```
🔄 Testing conditional: notifications checkbox

Before (unchecked):
  Visible: [name, status, budget, ...]
  Hidden: [notification_email, notification_frequency]

After (checked):
  Visible: [name, status, budget, notification_email, notification_frequency, ...]
  Hidden: []

📸 Screenshots captured: before/after
```

Record in `ui-states/form.json`:
```json
{
  "trigger": "notifications checkbox",
  "type": "checkbox",
  "before_state": {
    "hidden_fields": ["notification_email", "notification_frequency"]
  },
  "after_state": {
    "visible_fields": ["notification_email", "notification_frequency"],
    "new_validation": {
      "notification_email": "required|email"
    }
  }
}
```

### 3.4 Test Form Validation

**Empty submission test:**
```
🧪 Testing: Empty form submission

Clicking "Save" with empty form...

Validation errors found:
  • name: "The name field is required"
  • start_date: "Please select a start date"
  • end_date: "Please select an end date"

📸 Screenshot: validation-errors.png
```

**Invalid data test:**
```
🧪 Testing: Invalid data

Filling form with invalid values:
  • budget: -100 (negative)
  • end_date: before start_date
  • name: "x" (too short)

Errors found:
  • budget: "Budget must be at least 0"
  • end_date: "End date must be after start date"
  • name: "Name must be at least 3 characters"

📸 Screenshot: validation-invalid.png
```

### 3.5 Test Successful Submission

```
🧪 Testing: Valid submission

Filling form with valid test data:
  • name: "Test Campaign 12345"
  • status: "draft"
  • start_date: tomorrow
  • end_date: next week
  • budget: 1000

Clicking "Save as Draft"...

Result:
  • Redirected to: /campaigns/abc123
  • Toast message: "Campaign created successfully"
  • New record visible in list

📸 Screenshots: form-filled.png, success-redirect.png
```

### 3.6 Track Cross-Page Effects

```
🔗 Cross-page effects:

After creating campaign:
  • Appears in /campaigns list ✓
  • Count in sidebar updated: 5 → 6 ✓
  • Dashboard widget updated ✓

After editing campaign:
  • Changes reflected in list ✓
  • Detail page updated ✓

After deleting campaign:
  • Removed from list ✓
  • Related metrics deleted ✓
```

---

## STEP 4: SAVE EXPLORATION RESULTS

Update `docs/.knowledge/modules/{module}/`:

### interactions.json
```json
{
  "page": "/campaigns/create",
  "explored_at": "2024-01-15T10:30:00Z",
  "elements": {
    "forms": [...],
    "buttons": [...],
    "conditionals": [...]
  },
  "validation_discovered": {
    "name": {
      "rules": ["required", "min:3", "max:255"],
      "messages": {
        "required": "The name field is required",
        "min": "Name must be at least 3 characters"
      }
    }
  }
}
```

### ui-states/{page}.json
```json
{
  "page": "/campaigns/create",
  "states": {
    "initial": {...},
    "notifications_enabled": {...},
    "validation_error": {...},
    "submitting": {...},
    "success": {...}
  },
  "screenshots": {
    "initial": "explore/campaigns-create-initial.png",
    "notifications_enabled": "explore/campaigns-create-notifications.png",
    "validation_error": "explore/campaigns-create-errors.png",
    "success": "explore/campaigns-create-success.png"
  }
}
```

### cross-page-effects.json
```json
{
  "module": "campaigns",
  "effects": [
    {
      "action": "create",
      "affects": [
        {"page": "/campaigns", "change": "new item in list"},
        {"page": "/dashboard", "change": "campaign count updated"}
      ]
    },
    {
      "action": "delete",
      "affects": [
        {"page": "/campaigns", "change": "item removed"},
        {"page": "/metrics", "change": "related metrics removed"}
      ]
    }
  ]
}
```

---

## STEP 5: EXPLORATION SUMMARY

```
✅ Exploration Complete: {module}

📊 Results:
   Pages explored: 4
   Forms tested: 2
   Conditional triggers: 5
   Validation rules discovered: 12
   Cross-page effects: 8

📸 Screenshots captured: 15
   Saved to: docs/.knowledge/modules/{module}/screenshots/

📁 Files updated:
   • modules/{module}/interactions.json
   • modules/{module}/ui-states/list.json
   • modules/{module}/ui-states/form.json
   • modules/{module}/cross-page-effects.json
   • modules/{module}/validation-discovered.json

🔍 Key Findings:
   • notifications checkbox reveals 2 additional fields
   • status=active requires budget (conditional validation)
   • Creating campaign updates 3 other pages

💡 Next Steps:
   /docs:flow {module} --lifecycle    # Document full CRUD flow
   /docs:generate /{module}/create    # Generate create form docs
```

---

## DEPTH LEVELS

### --depth shallow
- Click main buttons only
- Test form with valid data once
- Capture initial/success states

### --depth medium (default)
- Test all visible interactive elements
- Test form validation (empty + invalid)
- Test all conditional triggers
- Track immediate cross-page effects

### --depth deep
- All of medium, plus:
- Test edge cases (max values, special characters)
- Test authorization (try accessing without permission)
- Test concurrent actions
- Test undo/redo if available
- Full state machine mapping

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Page not found | Skip, log to warnings |
| Auth required | Use config credentials or ask |
| Element not clickable | Try scrolling, wait, retry |
| Timeout | Capture current state, continue |
| Form submission creates real data | Warn user, offer to clean up |
