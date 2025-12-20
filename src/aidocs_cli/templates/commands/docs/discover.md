---
name: docs:discover
description: Scan codebase to discover all modules and their structure
---

# Discover All Modules

Scan your codebase to discover all modules/entities. Run this after `/docs:init`.

**Usage:**
```
/docs:discover                     # Discover all modules
/docs:discover --dry               # Preview without saving
/docs:discover campaigns           # Analyze only one module
```

**What it does:**
1. Scans backend for models, controllers, routes
2. Scans frontend for pages, components
3. Identifies relationships between modules
4. Saves analysis to `docs/.knowledge/`

**Output:**
```
docs/.knowledge/
├── _meta/
│   ├── project.json
│   └── modules-index.json      # List of all discovered modules
└── modules/
    ├── campaigns/
    │   ├── entity.json
    │   ├── routes.json
    │   └── components.json
    ├── users/
    └── orders/
```

**Next step:** Run `/docs:plan` to create documentation plan

---

**Execute workflow:** `@docs-workflows/discover/workflow.md`

**Knowledge Base Structure:**
```
docs/.knowledge/
├── _meta/
│   ├── project.json              # Project-level info
│   ├── stack.json                # Tech stack details
│   └── modules-index.json        # List of discovered modules
│
├── modules/
│   ├── {module-name}/            # e.g., campaigns/, users/, orders/
│   │   ├── entity.json           # Entity definition, fields, types
│   │   ├── routes.json           # Backend routes for this module
│   │   ├── components.json       # Frontend components
│   │   ├── validation.json       # Validation rules from code
│   │   ├── api-endpoints.json    # API endpoints with request/response
│   │   ├── flows/
│   │   │   ├── create.json       # Create flow steps
│   │   │   ├── edit.json         # Edit flow steps
│   │   │   ├── delete.json       # Delete flow steps
│   │   │   └── custom/           # Custom flows for this module
│   │   └── ui-states/
│   │       ├── list.json         # List page UI states
│   │       ├── form.json         # Form UI states & conditionals
│   │       └── detail.json       # Detail page UI states
│   │
│   └── {another-module}/
│       └── ...
│
├── relationships/
│   ├── {entity}-{entity}.json    # e.g., campaign-user.json
│   └── ...                       # Explicit relationship definitions
│
└── cross-module-flows/
    ├── {flow-name}.json          # e.g., checkout.json, onboarding.json
    └── ...                       # Flows spanning multiple modules
```

**What it analyzes:**

### Backend Analysis
- Models/Entities → fields, types, relationships, fillable/guarded
- Routes → endpoints, methods, middleware, controllers
- Controllers → actions, validation, business logic
- Validation → rules, custom validators, error messages
- Events/Listeners → side effects, notifications
- Policies → authorization rules

### Frontend Analysis
- Pages/Views → route mapping, layout, components used
- Components → props, events, slots, state
- Forms → fields, validation, conditional logic
- State Management → stores, actions, getters
- API Calls → endpoints used, request/response handling

### Relationship Discovery
- Database foreign keys
- Eloquent/ORM relationships
- Frontend data dependencies
- Cross-module navigation

---

**Execute workflow:** `@docs-workflows/discover/workflow.md`
