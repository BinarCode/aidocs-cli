---
name: docs-discover
description: Incremental module analysis to build knowledge graph - one module at a time.
---

# Discovery Workflow

**Goal:** Analyze a single module/entity to build its knowledge base. Works incrementally for large projects.

**Your Role:** You are a code analyst. You will analyze the specified module, extract its properties, understand its structure, and create structured JSON files.

---

## ARGUMENTS PARSING

Parse the arguments:
```
/docs:discover <module> [--deep] [--with-flows] [--list] [--refresh]
```

- `module` - Required (unless --list): Module name to analyze
- `--list` - Just list detectable modules, don't analyze
- `--deep` - Include relationship analysis
- `--with-flows` - Detect user flows
- `--refresh` - Overwrite existing analysis

**If no module provided and no --list:**
```
Please specify a module to analyze:
  /docs:discover campaigns
  /docs:discover users --deep

Or list available modules:
  /docs:discover --list
```

---

## STEP 1: SETUP / LIST MODULES

### If --list flag provided:

Quick scan to identify all modules without deep analysis:

**For Laravel:**
```bash
# List all models
ls app/Models/*.php | xargs -I {} basename {} .php

# List all controllers
ls app/Http/Controllers/*.php | sed 's/Controller.php//'
```

**For Vue/Nuxt:**
```bash
# List page directories
ls -d pages/*/ 2>/dev/null | xargs -I {} basename {}
```

**Output:**
```
📋 Detected Modules

From Backend (Models):
  • Campaign
  • User
  • Order
  • Product
  • Payment

From Frontend (Pages):
  • campaigns
  • users
  • orders
  • settings
  • dashboard

To analyze a module:
  /docs:discover campaigns
  /docs:discover users --deep
```

**Then STOP** - don't proceed with analysis.

---

### If module provided:

Create `docs/.knowledge/` structure if not exists:
```
docs/.knowledge/
├── _meta/
├── modules/
├── relationships/
└── cross-module-flows/
```

Check if module already analyzed:
- If exists and no `--refresh`: Ask "Module already analyzed. Use --refresh to re-analyze?"
- If `--refresh` or not exists: Proceed

---

## STEP 2: ANALYZE SINGLE MODULE

### 2.1 Backend Entity Discovery

**For Laravel/PHP:**
```bash
# Find all models
find app/Models -name "*.php"

# Find all controllers
find app/Http/Controllers -name "*Controller.php"

# Find route files
cat routes/web.php routes/api.php
```

**For Node.js/Express:**
```bash
# Find model definitions
find . -path "./node_modules" -prune -o -name "*.model.*" -print

# Find controllers/handlers
find . -name "*.controller.*" -o -name "*.handler.*"
```

**For each entity found, extract:**
- Entity name (singular, plural)
- Database table name
- Fields and types
- Relationships (belongsTo, hasMany, etc.)
- Fillable/guarded fields
- Casts and accessors

### 2.2 Frontend Module Discovery

**For Vue/Nuxt:**
```bash
# Find pages
find pages -name "*.vue" -o -name "*.tsx"

# Find components per module
find components -type d
```

**For React/Next:**
```bash
# Find pages
find app -name "page.tsx" -o -name "page.jsx"
find pages -name "*.tsx" -o -name "*.jsx"
```

**Map frontend to backend:**
- `/campaigns` page → `Campaign` entity
- `/users/[id]` page → `User` entity

### 2.3 Create Module Index

Create `docs/.knowledge/_meta/modules-index.json`:
```json
{
  "discovered_at": "2024-01-15T10:30:00Z",
  "modules": [
    {
      "name": "campaigns",
      "entity": "Campaign",
      "has_crud": true,
      "pages": ["/campaigns", "/campaigns/create", "/campaigns/[id]"],
      "api_prefix": "/api/campaigns"
    },
    {
      "name": "users",
      "entity": "User",
      "has_crud": true,
      "pages": ["/users", "/users/[id]/edit"],
      "api_prefix": "/api/users"
    }
  ]
}
```

---

## STEP 3: ANALYZE EACH MODULE

For each discovered module, create its folder and analyze in depth:

### 3.1 Entity Analysis

Create `modules/{name}/entity.json`:
```json
{
  "name": "Campaign",
  "table": "campaigns",
  "primary_key": "id",
  "timestamps": true,
  "soft_deletes": true,
  "fields": [
    {
      "name": "id",
      "type": "uuid",
      "primary": true
    },
    {
      "name": "name",
      "type": "string",
      "max_length": 255,
      "required": true
    },
    {
      "name": "status",
      "type": "enum",
      "values": ["draft", "active", "paused", "completed"],
      "default": "draft"
    },
    {
      "name": "budget",
      "type": "decimal",
      "precision": 10,
      "scale": 2,
      "nullable": true
    },
    {
      "name": "user_id",
      "type": "foreign_key",
      "references": "users.id",
      "relationship": "belongs_to"
    },
    {
      "name": "settings",
      "type": "json",
      "structure": {
        "notifications": "boolean",
        "auto_pause": "boolean",
        "daily_limit": "integer|null"
      }
    }
  ],
  "relationships": [
    {
      "type": "belongs_to",
      "related": "User",
      "foreign_key": "user_id"
    },
    {
      "type": "has_many",
      "related": "CampaignMetric",
      "foreign_key": "campaign_id"
    },
    {
      "type": "belongs_to_many",
      "related": "Tag",
      "pivot_table": "campaign_tag"
    }
  ],
  "scopes": ["active", "byUser", "withMetrics"],
  "accessors": ["formatted_budget", "is_active"],
  "mutators": ["name"]
}
```

### 3.2 Routes Analysis

Create `modules/{name}/routes.json`:
```json
{
  "module": "campaigns",
  "routes": [
    {
      "method": "GET",
      "uri": "/api/campaigns",
      "name": "campaigns.index",
      "controller": "CampaignController@index",
      "middleware": ["auth:sanctum"],
      "description": "List all campaigns for authenticated user",
      "query_params": [
        {"name": "status", "type": "string", "enum": ["draft", "active"]},
        {"name": "page", "type": "integer"},
        {"name": "per_page", "type": "integer", "default": 15}
      ],
      "response": {
        "type": "paginated",
        "resource": "CampaignResource"
      }
    },
    {
      "method": "POST",
      "uri": "/api/campaigns",
      "name": "campaigns.store",
      "controller": "CampaignController@store",
      "middleware": ["auth:sanctum"],
      "validation": "StoreCampaignRequest",
      "description": "Create a new campaign",
      "side_effects": [
        "Dispatches CampaignCreated event",
        "Sends notification to admin"
      ]
    },
    {
      "method": "PUT",
      "uri": "/api/campaigns/{campaign}",
      "name": "campaigns.update",
      "controller": "CampaignController@update",
      "middleware": ["auth:sanctum", "can:update,campaign"],
      "validation": "UpdateCampaignRequest"
    },
    {
      "method": "DELETE",
      "uri": "/api/campaigns/{campaign}",
      "name": "campaigns.destroy",
      "controller": "CampaignController@destroy",
      "middleware": ["auth:sanctum", "can:delete,campaign"],
      "soft_delete": true,
      "side_effects": [
        "Cascades to campaign_metrics",
        "Dispatches CampaignDeleted event"
      ]
    }
  ]
}
```

### 3.3 Validation Analysis

Create `modules/{name}/validation.json`:
```json
{
  "module": "campaigns",
  "requests": {
    "StoreCampaignRequest": {
      "rules": {
        "name": ["required", "string", "max:255", "unique:campaigns,name"],
        "status": ["sometimes", "in:draft,active,paused"],
        "budget": ["nullable", "numeric", "min:0", "max:1000000"],
        "start_date": ["required", "date", "after:today"],
        "end_date": ["required", "date", "after:start_date"],
        "user_id": ["required", "exists:users,id"],
        "tags": ["array"],
        "tags.*": ["exists:tags,id"],
        "settings.notifications": ["boolean"],
        "settings.daily_limit": ["nullable", "integer", "min:1"]
      },
      "messages": {
        "name.unique": "A campaign with this name already exists.",
        "end_date.after": "End date must be after the start date.",
        "budget.max": "Budget cannot exceed $1,000,000."
      },
      "conditional_rules": [
        {
          "condition": "status === 'active'",
          "adds": {
            "budget": ["required", "min:100"]
          },
          "description": "Active campaigns require a minimum budget of $100"
        }
      ]
    },
    "UpdateCampaignRequest": {
      "rules": {
        "name": ["sometimes", "string", "max:255"],
        "status": ["sometimes", "in:draft,active,paused,completed"]
      },
      "conditional_rules": [
        {
          "condition": "current_status === 'active' && new_status === 'draft'",
          "blocks": true,
          "message": "Cannot revert an active campaign to draft"
        }
      ]
    }
  }
}
```

### 3.4 Components Analysis

Create `modules/{name}/components.json`:
```json
{
  "module": "campaigns",
  "components": [
    {
      "name": "CampaignForm",
      "file": "components/campaigns/CampaignForm.vue",
      "type": "form",
      "props": [
        {"name": "campaign", "type": "Campaign|null", "required": false},
        {"name": "mode", "type": "'create'|'edit'", "default": "create"}
      ],
      "emits": ["submit", "cancel"],
      "fields": [
        {
          "name": "name",
          "component": "TextInput",
          "validation": "required|max:255"
        },
        {
          "name": "status",
          "component": "SelectInput",
          "options_from": "statusOptions"
        },
        {
          "name": "budget",
          "component": "NumberInput",
          "conditional": {
            "show_when": "status !== 'draft'",
            "required_when": "status === 'active'"
          }
        },
        {
          "name": "settings.notifications",
          "component": "Checkbox",
          "triggers": [
            {
              "when": "checked",
              "shows": ["settings.notification_email", "settings.notification_frequency"]
            }
          ]
        }
      ],
      "api_calls": [
        {"action": "submit", "endpoint": "POST /api/campaigns"},
        {"action": "submit (edit)", "endpoint": "PUT /api/campaigns/{id}"}
      ]
    },
    {
      "name": "CampaignList",
      "file": "components/campaigns/CampaignList.vue",
      "type": "list",
      "data_source": "GET /api/campaigns",
      "columns": ["name", "status", "budget", "created_at"],
      "actions": [
        {"name": "edit", "navigates_to": "/campaigns/{id}/edit"},
        {"name": "delete", "confirms": true, "endpoint": "DELETE /api/campaigns/{id}"}
      ],
      "filters": ["status", "date_range"],
      "pagination": true
    }
  ]
}
```

### 3.5 UI States Analysis

Create `modules/{name}/ui-states/form.json`:
```json
{
  "component": "CampaignForm",
  "states": {
    "initial": {
      "description": "Empty form ready for input",
      "visible_fields": ["name", "status", "start_date", "end_date"],
      "hidden_fields": ["budget", "settings.notification_email"],
      "buttons": ["Cancel", "Save as Draft"]
    },
    "status_active": {
      "trigger": "status field changed to 'active'",
      "changes": {
        "shows": ["budget"],
        "budget_required": true,
        "buttons": ["Cancel", "Save", "Save & Activate"]
      }
    },
    "notifications_enabled": {
      "trigger": "settings.notifications checkbox checked",
      "changes": {
        "shows": ["settings.notification_email", "settings.notification_frequency"],
        "adds_validation": {
          "settings.notification_email": "required|email"
        }
      }
    },
    "has_budget": {
      "trigger": "budget field has value > 0",
      "changes": {
        "shows": ["settings.daily_limit", "settings.auto_pause"]
      }
    },
    "submitting": {
      "description": "Form is being submitted",
      "buttons_disabled": true,
      "shows_spinner": true
    },
    "validation_error": {
      "description": "Server returned validation errors",
      "shows_errors": true,
      "scroll_to_first_error": true
    },
    "success": {
      "description": "Form submitted successfully",
      "redirects_to": "/campaigns/{id}",
      "shows_toast": "Campaign created successfully"
    }
  },
  "state_transitions": [
    {"from": "initial", "to": "status_active", "via": "select status = active"},
    {"from": "initial", "to": "notifications_enabled", "via": "check notifications"},
    {"from": "*", "to": "submitting", "via": "click submit"},
    {"from": "submitting", "to": "validation_error", "via": "422 response"},
    {"from": "submitting", "to": "success", "via": "201 response"}
  ]
}
```

---

## STEP 4: DISCOVER RELATIONSHIPS

For each relationship found in entities:

Create `relationships/{entity1}-{entity2}.json`:
```json
{
  "entities": ["Campaign", "User"],
  "relationship_type": "belongs_to",
  "description": "Each campaign belongs to one user (the creator)",
  "foreign_key": {
    "table": "campaigns",
    "column": "user_id",
    "references": "users.id"
  },
  "cascade": {
    "on_delete": "cascade",
    "on_update": "cascade"
  },
  "ui_implications": [
    "Campaign list shows owner name",
    "User profile shows their campaigns",
    "Deleting user deletes their campaigns"
  ],
  "navigation": [
    {"from": "/campaigns/{id}", "to": "/users/{user_id}", "via": "owner link"},
    {"from": "/users/{id}", "to": "/campaigns?user={id}", "via": "campaigns tab"}
  ]
}
```

---

## STEP 5: IDENTIFY CROSS-MODULE FLOWS

Look for flows that span multiple modules:

Create `cross-module-flows/{flow-name}.json`:
```json
{
  "name": "Campaign Creation with Budget Approval",
  "description": "When a campaign exceeds budget threshold, it requires manager approval",
  "modules_involved": ["campaigns", "users", "approvals", "notifications"],
  "trigger": "Campaign created with budget > $10,000",
  "steps": [
    {
      "step": 1,
      "module": "campaigns",
      "action": "User submits campaign form",
      "page": "/campaigns/create"
    },
    {
      "step": 2,
      "module": "campaigns",
      "action": "System detects high budget",
      "condition": "budget > 10000"
    },
    {
      "step": 3,
      "module": "approvals",
      "action": "Approval request created",
      "side_effect": "Creates ApprovalRequest record"
    },
    {
      "step": 4,
      "module": "notifications",
      "action": "Manager notified",
      "channels": ["email", "in-app"]
    },
    {
      "step": 5,
      "module": "approvals",
      "action": "Manager reviews",
      "page": "/approvals/{id}",
      "outcomes": ["approve", "reject", "request_changes"]
    },
    {
      "step": 6,
      "module": "campaigns",
      "action": "Campaign status updated",
      "if_approved": "status = 'active'",
      "if_rejected": "status = 'rejected'"
    }
  ],
  "data_flow": {
    "campaign_id": "Created in step 1, referenced in steps 3-6",
    "approval_id": "Created in step 3, used in step 5",
    "manager_id": "Determined by campaign.user.manager_id"
  }
}
```

---

## STEP 6: GENERATE SUMMARY

Create `docs/.knowledge/_meta/project.json`:
```json
{
  "analyzed_at": "2024-01-15T10:30:00Z",
  "project_name": "MyApp",
  "modules_count": 12,
  "entities_count": 15,
  "routes_count": 48,
  "components_count": 67,
  "relationships_count": 23,
  "cross_module_flows_count": 5,
  "coverage": {
    "entities_with_crud": 12,
    "entities_partial": 3,
    "orphan_components": 2
  }
}
```

**Display summary:**
```
✅ Discovery Complete

📊 Analysis Results:
   Modules discovered: 12
   Entities analyzed: 15
   Routes mapped: 48
   Components cataloged: 67
   Relationships found: 23
   Cross-module flows: 5

📁 Knowledge base created: docs/.knowledge/
   ├── _meta/          (project & stack info)
   ├── modules/        (12 module folders)
   ├── relationships/  (23 relationship files)
   └── cross-module-flows/ (5 flow files)

🔍 Key Findings:
   • Campaign module has complex conditional UI
   • Order → Payment has multi-step flow
   • User deletion cascades to 5 related entities

💡 Next Steps:
   1. Run /docs:explore to discover UI behaviors
   2. Run /docs:flow campaign to document campaign lifecycle
   3. Run /docs:generate to create documentation using this knowledge
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| No models found | Check stack detection, ask for model path |
| Ambiguous relationships | Create `relationships/_ambiguous.json` for manual review |
| Circular dependencies | Flag in `_meta/warnings.json` |
| Missing validation | Note in module's `validation.json` as "not found" |

---

## TIPS

- Run `/docs:discover` once at project setup, then incrementally with `--module`
- Review `_meta/warnings.json` for issues needing attention
- Knowledge base is used by `/docs:generate`, `/docs:flow`, `/docs:explore`
- Commit `docs/.knowledge/` to share with team
