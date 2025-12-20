---
name: docs-flow
description: Document a complete entity lifecycle or custom user flow with cross-page tracking and screenshots.
---

# Flow Documentation Workflow

**Goal:** Generate comprehensive step-by-step documentation for an entity's lifecycle (CRUD) or a custom user flow, capturing screenshots and tracking data across pages.

**Your Role:** You are a flow documentarian. You will execute a complete user journey, capture each step, document what happens, and produce a detailed guide.

**Requires:** Playwright MCP

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:flow <entity|"custom description"> [--lifecycle] [--include-errors] [--skip-explore] [--output]
```

Examples:
```
/docs:flow campaign                      # Smart detection of main flow
/docs:flow campaign --lifecycle          # Full CRUD: create, view, edit, delete
/docs:flow "user registration"           # Custom flow by description
/docs:flow order --include-errors        # Include error states
/docs:flow campaign --skip-explore       # Skip UI exploration (use existing knowledge)
```

---

## STEP 1: AUTO-RUN PREREQUISITES

**This command automatically runs discover and explore if needed.**

### 1.1 Check Knowledge Base

Check if `.docs-knowledge/modules/{entity}/` exists:

```
🔍 Checking knowledge base for: campaign

□ Module discovery    → Not found
□ UI exploration      → Not found
□ Flow documentation  → Starting...
```

### 1.2 Auto-Run Discover (if missing)

If knowledge base doesn't exist for this module:

```
📊 Step 1/3: Discovering module structure...

Running: /docs:discover campaign --deep

✓ Entity analyzed: Campaign (12 fields, 3 relationships)
✓ Routes found: 5 endpoints
✓ Validation rules: 8 rules extracted
✓ Components: CampaignForm, CampaignList, CampaignDetail

Knowledge saved to: .docs-knowledge/modules/campaigns/
```

### 1.3 Auto-Run Explore (if missing or outdated)

If UI exploration hasn't been done (unless --skip-explore):

```
🖱️ Step 2/3: Exploring UI behaviors...

Running: /docs:explore campaign

✓ Pages explored: 4
✓ Conditional UI discovered: 3 triggers
✓ Validation messages captured: 8
✓ Cross-page effects mapped: 5

Exploration saved to: .docs-knowledge/modules/campaigns/ui-states/
```

### 1.4 Proceed to Flow Documentation

```
📚 Step 3/3: Documenting flow...

Knowledge loaded:
  ✓ Entity: Campaign
  ✓ Routes: 5 endpoints
  ✓ UI States: 4 pages mapped
  ✓ Validation: 8 rules + messages

Ready to document flow.
```

---

## STEP 2: DETERMINE FLOW TYPE

### If entity name provided:

Load knowledge from `.docs-knowledge/modules/{entity}/`

**Detect available flows:**
```
📋 Available flows for: campaign

Standard CRUD:
  [1] Create campaign
  [2] View campaign
  [3] Edit campaign
  [4] Delete campaign
  [5] Full lifecycle (all above)

Detected custom flows:
  [6] Duplicate campaign
  [7] Archive campaign
  [8] Campaign approval (requires budget > $10k)

Which flow to document?
```

### If custom description provided:

Parse the description to understand:
- Starting point
- End goal
- Modules involved

```
📋 Planning flow: "user registration to first purchase"

Detected steps:
  1. /register - Create account
  2. /verify-email - Confirm email
  3. /onboarding - Complete profile
  4. /products - Browse products
  5. /cart - Add to cart
  6. /checkout - Complete purchase

Modules involved: users, products, orders, payments

Proceed with this flow? [Y/n]
```

---

## STEP 2: PREPARE FLOW EXECUTION

### 2.1 Load Prerequisites

```
🔧 Preparing flow: Create Campaign

Prerequisites:
  ✓ Authenticated user required
  ✓ Test data will be created
  ✓ Knowledge base loaded

⚠️  This flow will create real data in your application.
    Proceed? [Y/n/use test environment]
```

### 2.2 Define Test Data

Generate or ask for test data:
```
📝 Test data for campaign creation:

  name: "Documentation Test Campaign"
  status: "draft"
  budget: 5000
  start_date: 2024-02-01
  end_date: 2024-02-28
  tags: ["test", "documentation"]

Use this data? [Y/n/customize]
```

---

## STEP 3: EXECUTE FLOW WITH DOCUMENTATION

For each step in the flow:

### Step Template:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Step 1: Navigate to create page
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action: Click "New Campaign" button
URL: /campaigns → /campaigns/create

📸 Capturing screenshot: step-01-navigate.png

Observations:
  • Empty form displayed
  • 8 fields visible
  • "Save as Draft" and "Cancel" buttons

Conditional UI state: initial
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Full CRUD Lifecycle Example:

**STEP 1: Navigate to List**
```
📍 Starting point: /campaigns
📸 step-01-list-before.png

Observations:
  • Campaign list shows 5 existing campaigns
  • "New Campaign" button in top right
  • Filter/search available
```

**STEP 2: Open Create Form**
```
📍 Action: Click "New Campaign"
📍 URL: /campaigns/create
📸 step-02-create-form.png

Observations:
  • Form with 8 fields
  • Required fields marked with *
  • Default status: draft
```

**STEP 3: Fill Form**
```
📍 Action: Fill form fields
📸 step-03-form-filled.png

Data entered:
  • name: "Documentation Test Campaign"
  • budget: 5000
  • ...

Conditional changes observed:
  • Entering budget revealed "daily limit" field
```

**STEP 4: Submit Form**
```
📍 Action: Click "Save"
📍 Result: Redirected to /campaigns/abc123
📸 step-04-success.png

Observations:
  • Success toast: "Campaign created successfully"
  • Now viewing campaign detail page
  • All entered data displayed correctly
```

**STEP 5: Verify in List**
```
📍 Action: Navigate to /campaigns
📸 step-05-list-after.png

Observations:
  • New campaign appears in list
  • Count updated: 5 → 6
  • Filters work with new campaign
```

**STEP 6: Edit Campaign**
```
📍 Action: Click "Edit" on new campaign
📍 URL: /campaigns/abc123/edit
📸 step-06-edit-form.png

Observations:
  • Form pre-filled with current values
  • Can modify all fields
```

**STEP 7: Save Edit**
```
📍 Action: Change budget to 7500, click "Save"
📸 step-07-edit-success.png

Observations:
  • Redirected to detail page
  • Budget shows updated value
```

**STEP 8: Delete Campaign**
```
📍 Action: Click "Delete"
📸 step-08-delete-confirm.png

Observations:
  • Confirmation modal appears
  • "This action cannot be undone"
```

**STEP 9: Confirm Delete**
```
📍 Action: Click "Confirm Delete"
📍 Result: Redirected to /campaigns
📸 step-09-delete-success.png

Observations:
  • Campaign removed from list
  • Count updated: 6 → 5
  • Toast: "Campaign deleted"
```

---

## STEP 4: DOCUMENT ERROR STATES (if --include-errors)

### Validation Errors
```
📍 Error test: Submit empty form
📸 error-01-validation.png

Errors displayed:
  • name: "The name field is required"
  • start_date: "Please select a start date"

Behavior:
  • Form not submitted
  • First error field focused
  • Scroll to error
```

### Permission Errors
```
📍 Error test: Edit without permission
📸 error-02-permission.png

Result:
  • 403 Forbidden
  • Message: "You don't have permission to edit this campaign"
```

### Not Found
```
📍 Error test: View deleted campaign
📸 error-03-not-found.png

Result:
  • 404 page displayed
  • "Campaign not found"
  • Link back to list
```

---

## STEP 5: GENERATE FLOW DOCUMENTATION

Create markdown file in output directory:

### File: `docs/flows/campaign-lifecycle.md`

```markdown
# Campaign Lifecycle

This guide covers the complete lifecycle of a campaign: creating, viewing, editing, and deleting.

## Overview

Campaigns are the core entity for organizing your marketing efforts. Each campaign has a name, budget, date range, and various settings.

## Prerequisites

- Logged in as a user with campaign management permissions
- Access to the Campaigns section

---

## Creating a Campaign

### Step 1: Open the create form

From the campaigns list (`/campaigns`), click the **"New Campaign"** button in the top right corner.

![Campaign List](./images/campaign-flow-step-01.png)

### Step 2: Fill in the campaign details

Complete the form with your campaign information:

| Field | Required | Description |
|-------|----------|-------------|
| Name | Yes | Unique name for your campaign |
| Status | No | Draft (default), Active, or Paused |
| Budget | Conditional | Required when status is Active |
| Start Date | Yes | When the campaign begins |
| End Date | Yes | When the campaign ends |
| Tags | No | Organize campaigns with tags |

![Create Form](./images/campaign-flow-step-02.png)

> **Note:** When you enter a budget amount, additional fields for daily limit and auto-pause will appear.

### Step 3: Save the campaign

Click **"Save"** to create the campaign. You'll be redirected to the campaign detail page.

![Success](./images/campaign-flow-step-03.png)

---

## Viewing a Campaign

Click on any campaign in the list to view its details.

![Campaign Detail](./images/campaign-flow-detail.png)

The detail page shows:
- Campaign name and status
- Budget and date range
- Performance metrics (if active)
- Tags and settings

---

## Editing a Campaign

### Step 1: Open edit mode

From the campaign detail page, click **"Edit"** or click the edit icon in the list.

### Step 2: Modify fields

Update any fields as needed. Changes are not saved until you click Save.

![Edit Form](./images/campaign-flow-edit.png)

### Step 3: Save changes

Click **"Save"** to apply your changes.

> **Warning:** Changing status from Active to Draft may affect running ads.

---

## Deleting a Campaign

### Step 1: Initiate delete

Click **"Delete"** from the campaign detail page or the list actions menu.

### Step 2: Confirm deletion

A confirmation dialog will appear. Click **"Confirm Delete"** to proceed.

![Delete Confirmation](./images/campaign-flow-delete.png)

> **Warning:** This action cannot be undone. All campaign data and metrics will be permanently deleted.

---

## Common Issues

### "The name field is required"

All campaigns must have a name. Enter a unique name for your campaign.

### "Budget is required for active campaigns"

When setting status to "Active", you must specify a budget amount.

### "You don't have permission"

Contact your administrator to request campaign management permissions.

---

## Related

- [Campaign Settings](./campaign-settings.md)
- [Campaign Metrics](./campaign-metrics.md)
- [Bulk Campaign Operations](./campaign-bulk.md)

---

*Documentation generated by [aidocs-cli](https://github.com/binarcode/aidocs-cli) using /docs:flow*
```

---

## STEP 6: UPDATE KNOWLEDGE BASE

Save flow to `.docs-knowledge/modules/{entity}/flows/`:

### lifecycle.json
```json
{
  "flow": "lifecycle",
  "entity": "campaign",
  "documented_at": "2024-01-15T10:30:00Z",
  "steps": [
    {
      "step": 1,
      "action": "navigate_to_list",
      "url": "/campaigns",
      "screenshot": "campaign-flow-step-01.png"
    },
    {
      "step": 2,
      "action": "click_create",
      "url": "/campaigns/create",
      "screenshot": "campaign-flow-step-02.png"
    }
    // ... more steps
  ],
  "test_data_used": {
    "name": "Documentation Test Campaign",
    "budget": 5000
  },
  "errors_documented": ["validation", "permission", "not_found"],
  "output_file": "docs/flows/campaign-lifecycle.md"
}
```

---

## STEP 7: COMPLETION SUMMARY

```
✅ Flow Documentation Complete

📋 Flow: Campaign Lifecycle
📄 Output: docs/flows/campaign-lifecycle.md

📊 Coverage:
   Steps documented: 9
   Screenshots captured: 12
   Error states: 3
   Related pages: 5

📁 Files created:
   • docs/flows/campaign-lifecycle.md
   • docs/images/campaign-flow-step-*.png (12 images)

📁 Knowledge updated:
   • .docs-knowledge/modules/campaigns/flows/lifecycle.json

💡 Suggestions:
   • Run /docs:flow campaign-approval for the approval flow
   • Add this to your index: [Campaign Lifecycle](./flows/campaign-lifecycle.md)
```

---

## CLEANUP

After documenting:

```
🧹 Cleanup

Test data created during documentation:
  • Campaign: "Documentation Test Campaign" (ID: abc123)

Options:
  1. Delete test data (recommended)
  2. Keep test data
  3. Mark as test data (add [TEST] prefix)

Choice:
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Entity not found | Suggest /docs:discover first |
| Auth required | Use config credentials |
| Step failed | Capture error, continue or retry |
| Data creation failed | Log error, skip dependent steps |
