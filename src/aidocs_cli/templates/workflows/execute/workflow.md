---
name: docs-execute
description: Execute the documentation plan and generate all docs with screenshots
---

# Documentation Execution Workflow

**Goal:** Execute the documentation plan, generating comprehensive documentation for each module in order, with screenshots and cross-module flows.

**Your Role:** You are a documentation generator. You will systematically work through the plan, running explore and flow documentation for each module.

**Requires:**
- `docs-plan.yaml` from `/docs:plan`
- Playwright MCP for browser automation

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:execute [--module <name>] [--continue] [--dry]
```

Examples:
```
/docs:execute                      # Execute full plan
/docs:execute --module campaigns   # Execute only one module
/docs:execute --continue           # Continue from where it stopped
/docs:execute --dry                # Preview what would be generated
```

---

## STEP 1: LOAD PLAN

### 1.1 Read Plan File

```
📋 Loading documentation plan...

✓ Plan found: docs-plan.yaml
  Created: 2024-01-15 10:30:00
  Modules: 4
  Cross-module flows: 2
```

### 1.2 Check Plan Status

```
📊 Plan Status:

Modules:
  ○ users         - Pending
  ○ campaigns     - Pending
  ○ orders        - Pending
  ○ payments      - Pending

Cross-module flows:
  ○ user-registration-to-first-campaign - Pending
  ○ order-checkout-payment - Pending

Ready to execute.
```

If `--continue`:
```
📊 Resuming execution...

Modules:
  ✓ users         - Complete
  → campaigns     - Resuming...
  ○ orders        - Pending
  ○ payments      - Pending

Continuing from: campaigns
```

---

## STEP 2: VALIDATE PREREQUISITES

### 2.1 Check Playwright

```
🔧 Checking prerequisites...

✓ Playwright MCP available
✓ Authentication configured
✓ Output directory writable
```

### 2.2 Check Knowledge Base

For each module in plan, verify knowledge exists:

```
📁 Verifying knowledge base...

✓ users         - docs/.knowledge/modules/users/
✓ campaigns     - docs/.knowledge/modules/campaigns/
✓ orders        - docs/.knowledge/modules/orders/
✓ payments      - docs/.knowledge/modules/payments/

All modules have discovery data.
```

---

## STEP 3: DRY RUN (if --dry)

If `--dry` flag provided:

```
📋 Dry Run - Preview

Would generate:

docs/
├── index.md                              # Main index
├── users/
│   ├── index.md                          # Module overview
│   ├── lifecycle.md                      # CRUD documentation
│   └── images/                           # 8-12 screenshots
├── campaigns/
│   ├── index.md                          # Module overview
│   ├── lifecycle.md                      # CRUD documentation
│   ├── duplicate-campaign.md             # Custom flow
│   ├── archive-campaign.md               # Custom flow
│   └── images/                           # 15-20 screenshots
├── orders/
│   ├── index.md                          # Module overview
│   ├── lifecycle.md                      # CRUD documentation
│   └── images/                           # 8-12 screenshots
└── payments/
    ├── index.md                          # Module overview
    ├── lifecycle.md                      # CRUD documentation
    └── images/                           # 6-10 screenshots

Note: Cross-module flows are placed in the first module's folder:
  • users/user-registration-to-first-campaign.md
  • orders/order-checkout-payment.md

Estimated:
  • 12 markdown files
  • 40-50 screenshots
  • 4 image directories

Continue with actual execution? [Y/n]
```

---

## STEP 4: EXECUTE MODULE DOCUMENTATION

For each module in priority order:

### 4.1 Start Module

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 [1/4] Documenting: users
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority: 1 (Core module)
Knowledge: docs/.knowledge/modules/users/
Output: docs/users/

Starting documentation...
```

### 4.2 Run Explore (if UI not explored)

Check if UI exploration exists:

```
🖱️ Exploring UI...

  Navigating to /users
  📸 Capturing list page...

  Navigating to /users/create
  📸 Capturing create form...
  🔍 Testing conditional fields...
  ⚠️  Testing validation...

  ✓ UI exploration complete
    Pages explored: 4
    Screenshots: 8
    Validation messages: 5
    Conditional triggers: 2
```

### 4.3 Generate Lifecycle Documentation

```
📚 Generating lifecycle documentation...

  ✓ Overview section
  ✓ Create flow (4 steps, 4 screenshots)
  ✓ View flow (2 steps, 2 screenshots)
  ✓ Edit flow (3 steps, 3 screenshots)
  ✓ Delete flow (2 steps, 2 screenshots)
  ✓ Error states (3 scenarios)
  ✓ Field reference table

  Written: docs/users/lifecycle.md
```

### 4.4 Generate Module Index

```
📄 Generating module index...

  ✓ Module overview
  ✓ Features list
  ✓ Navigation links
  ✓ Related modules

  Written: docs/users/index.md
```

### 4.5 Generate Custom Flows (if any)

If module has custom flows defined:

```
📚 Generating custom flows...

  [1/2] duplicate campaign
    ✓ Flow documented (6 steps, 6 screenshots)
    Written: docs/campaigns/duplicate-campaign.md

  [2/2] archive campaign
    ✓ Flow documented (4 steps, 4 screenshots)
    Written: docs/campaigns/archive-campaign.md
```

### 4.6 Update Plan Status

```
✓ Module complete: users

Updating plan status...
  users: pending → complete

Progress: 1/4 modules complete
```

---

## STEP 5: PROGRESS DISPLAY

Show ongoing progress:

```
📋 Executing Documentation Plan

[1/4] users
  ✓ Exploring UI..............done
  ✓ Documenting lifecycle.....done
  ✓ Screenshots captured: 11
  ✓ Written: docs/users/

[2/4] campaigns
  ✓ Exploring UI..............done
  ✓ Documenting lifecycle.....done
  ✓ Documenting custom flows..done
  ✓ Screenshots captured: 18
  ✓ Written: docs/campaigns/

[3/4] orders
  → Exploring UI..............in progress

Status: 2 complete, 1 in progress, 1 pending
Time elapsed: 4m 23s
```

---

## STEP 6: CROSS-MODULE FLOWS

After all modules complete, document cross-module flows:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Cross-Module Flows
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/2] User Registration to First Campaign
  Modules: users → campaigns

  → Navigating user registration flow...
  📸 Step 1: Register page
  📸 Step 2: Fill form
  📸 Step 3: Verify email
  📸 Step 4: Complete profile
  → Transitioning to campaigns...
  📸 Step 5: Create first campaign
  📸 Step 6: Campaign created

  ✓ Flow documented (6 steps, 6 screenshots)
  Written: docs/users/user-registration-to-first-campaign.md

[2/2] Order Checkout to Payment
  Modules: orders → payments

  → Navigating checkout flow...
  📸 Step 1: Cart review
  📸 Step 2: Shipping
  📸 Step 3: Payment method
  📸 Step 4: Confirm order
  📸 Step 5: Payment processing
  📸 Step 6: Order complete

  ✓ Flow documented (6 steps, 6 screenshots)
  Written: docs/orders/order-checkout-payment.md
```

---

## STEP 7: GENERATE MAIN INDEX

Create/update the main documentation index:

```
📄 Generating main index...

docs/index.md:

# [Project Name] Documentation

## Modules

| Module | Description | Documentation |
|--------|-------------|---------------|
| Users | User management and authentication | [View](./users/) |
| Campaigns | Marketing campaign management | [View](./campaigns/) |
| Orders | Order processing and fulfillment | [View](./orders/) |
| Payments | Payment handling | [View](./payments/) |

## User Flows

- [User Registration to First Campaign](./users/user-registration-to-first-campaign.md)
- [Order Checkout to Payment](./orders/order-checkout-payment.md)

---

*Generated by [aidocs-cli](https://github.com/binarcode/aidocs-cli)*

✓ Written: docs/index.md
```

---

## STEP 8: UPDATE PLAN STATUS

Mark plan as complete:

```yaml
# docs-plan.yaml (updated)

status: complete
completed_at: 2024-01-15T11:45:00Z

modules:
  - name: users
    status: complete
    completed_at: 2024-01-15T10:45:00Z

  - name: campaigns
    status: complete
    completed_at: 2024-01-15T11:00:00Z

  - name: orders
    status: complete
    completed_at: 2024-01-15T11:20:00Z

  - name: payments
    status: complete
    completed_at: 2024-01-15T11:35:00Z

cross_module_flows:
  - name: "user-registration-to-first-campaign"
    status: complete
    completed_at: 2024-01-15T11:40:00Z

  - name: "order-checkout-payment"
    status: complete
    completed_at: 2024-01-15T11:45:00Z
```

---

## STEP 9: COMPLETION SUMMARY

```
✅ Documentation Generation Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary:
   Modules documented: 4
   Custom flows: 2
   Cross-module flows: 2
   Total screenshots: 52
   Time elapsed: 15m 23s

📁 Output:
   docs/
   ├── index.md
   ├── users/           (4 files, 14 images)
   ├── campaigns/       (5 files, 18 images)
   ├── orders/          (4 files, 15 images)
   └── payments/        (3 files, 8 images)

📄 Files created: 16 markdown files
📸 Screenshots: 52 images

💡 Next steps:
   • Review generated documentation
   • Customize as needed
   • Commit to repository

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ERROR HANDLING & RECOVERY

### Handle Failures

If a step fails:

```
❌ Error during: campaigns/lifecycle

Error: Navigation timeout at /campaigns/create

Options:
  [1] Retry this step
  [2] Skip this module, continue with next
  [3] Save progress and stop

Choice:
```

### Save Progress

Progress is saved after each module completes. The plan file tracks:
- Which modules are complete
- Which are in progress
- Where to resume

### Resume Execution

```
/docs:execute --continue

📋 Resuming from saved progress...

Completed:
  ✓ users
  ✓ campaigns

Resuming:
  → orders (starting fresh)
  ○ payments (pending)

Continue? [Y/n]
```

---

## MODULE-SPECIFIC EXECUTION

If `--module <name>` provided:

```
/docs:execute --module campaigns

📋 Executing single module: campaigns

Skipping other modules in plan.
Only documenting: campaigns

[1/1] campaigns
  → Exploring UI...
  ...
```

---

## CLEANUP

After completion:

```
🧹 Cleanup

Test data created during documentation:
  • User: test_doc_user@example.com
  • Campaign: "Documentation Test Campaign"
  • Order: #DOC-12345

Options:
  [1] Delete test data (recommended)
  [2] Keep test data
  [3] Mark as test data (add [TEST] prefix)

Choice:
```

---

## ERROR CODES

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Plan not found |
| 2 | Prerequisites missing |
| 3 | Module documentation failed |
| 4 | User cancelled |
